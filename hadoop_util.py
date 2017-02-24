from general_util import *


class NodesSpecificationError(Exception):
    def __init__(self,message):
        super(NodesSpecificationError,self).__init__("Wrong specification for nodes: {0}".format(message))
        self.message = message

# check the correctness of the parameters pass to create a hadoop cluster
def validate_cluster_parameters(nodes,ndatanodes,nnodemanagers,colocated):
    """

    :rtype: NodesSpecificationError exception if the cluster parameters doesn't make sense
    """
    if colocated:
        if (nnodemanagers>len(nodes)-1):
            raise NodesSpecificationError("Colocated: Number of nodemanagers greater than the number of nodes minus master node")
        if (ndatanodes>len(nodes)):
            raise NodesSpecificationError("Colocated: Number of datanodes greater than the number of nodes")
        if (ndatanodes<len(nodes) and nnodemanagers<len(nodes)-1):
            raise NodesSpecificationError("Colocated: The are fewer nodes reserved than roles specified")
    if not colocated:
        if (nnodemanagers+ndatanodes>len(nodes)):
            raise NodesSpecificationError("Not Colocated: Number of nodemanagers plus datanodes greater than the number of nodes")
        if (nnodemanagers+ndatanodes<len(nodes)):
            raise NodesSpecificationError("Not Colocated: The are fewer nodes reserved than roles specified")



##
##CURRENT LOGIC IS: IF COLOCATED, MAKE THE MASTER THE ONE WITH THE LEAST AMOUNT OF RAM, THE NODEMANAGERS THE N NODES WITH THE MOST AMMOUNT OF RAM AND THE DATANODES THE ONES WITH THE MOST STORAGE
##                  IF NOT COLOCATED, MAKE THE MASTER THE ONE WITH THE LEAST AMOUNT OF RAM, THE DATANODES THE ONES WITH THE MOST STORAGE AND THE ONES THAT ARE NOT MASTER NEITHER DATANODES AS NODEMANAGERS
def split_hadoop_roles(nodesDF,nDatanodes,nNodemanagers,colocated):
    if colocated:
        master = node_with_smaller_memory(nodesDF) ## The node with the smaller memory is the master
        nodemanagers = nodes_with_largest_memory(nodesDF[nodesDF["node_name"]!=list(master)[0]],nNodes=nNodemanagers) # the nodes that are not the master ((nodesDF[nodesDF["node_name"]!=list(master)[0]) are nodemanagers
        datanodes = set() ## Let's assign the datanodes. We use sets because it will allow us to do intersections and unions
        largest_storage_nodes = nodes_with_largest_storage(nodesDF,nNodes=nDatanodes)
        intersection = nodemanagers.intersection(largest_storage_nodes)
        if (len(intersection) < nDatanodes): ## If the intersection of the nodemanagers and the largest storage nodes is less thant the number of datanodes...
            if largest_storage_nodes>=nodemanagers:
                datanodes.update(largest_storage_nodes)
            else:
                additional = nDatanodes - len(intersection) ## the number of datanodes we have to add
                disjoint = [list(nodemanagers.difference(largest_storage_nodes))[i] for i in range(additional)] ## we take N number of datanodes from the difference between nodemanagers and largest storage
                datanodes.update(intersection)
                datanodes.update(set(disjoint))
        else:
            datanodes = nodemanagers.union(largest_storage_nodes)
    else:
        master = node_with_smaller_memory(nodesDF) # The node with the smaller memory is the master
        nodemanagers = nodes_with_largest_memory(nodesDF[nodesDF["node_name"]!=list(master)[0]],nNodes=nNodemanagers) # the nodes that are not the master ((nodesDF[nodesDF["node_name"]!=list(master)[0]) are nodemanagers
        datanodes = nodes_with_largest_storage(nodesDF[~nodesDF["node_name"].isin(list(nodemanagers))],nNodes=nDatanodes)  # The first n nodes with more storage space are datanodes
    return datanodes, nodemanagers, master

### (nodes: DF with all the nodes in the reservation, datanodes, nodemanagers, master: An iterable with the name of the nodes, osMemory: the ammount of memory we want to leave free for OS)
def install_hadoop(nodesDF,masternode,nodemanagers,osMemory):
    all_hosts = nodesDF.node_name.tolist()
    tarball_url = "http://www.eu.apache.org/dist/hadoop/common/hadoop-2.6.0/hadoop-2.6.0.tar.gz" ## whatever version we want
    #   {BEGIN}DEFINE THE DIFFERENT LOCAL PATHS
    path_core_site_template = "hadoop-resources/templates/core-site.xml.template"
    path_core_site_tmp = "hadoop-resources/tmp/core-site.xml"
    path_yarn_site_template = "hadoop-resources/templates/yarn-site.xml.template"
    path_yarn_site_tmp = "hadoop-resources/tmp/yarn-site.xml"
    path_mapred_site_template = "hadoop-resources/templates/mapred-site.xml.template"
    #   {END}DEFINE THE DIFFERENT LOCAL PATHS
    hadoop_home = "/opt/hadoop" ## The directory where we are going to install hadoop in g5k
    hadoop_conf = hadoop_home + "/etc/hadoop"
    Remote("wget {url} -O {destination}/hadoop.tar.gz 2>1".format(url=tarball_url,destination=wget_destination),
           hosts=all_hosts,connection_params={'user': 'root'}).run() ## Download the hadoop distribution on it
    Remote("cd {0} && tar -xvzf hadoop.tar.gz".format(wget_destination),hosts=all_hosts,
           connection_params={'user': 'root'}).run() ## untar Hadoop
    Remote("cd {0} && mv hadoop-* hadoop".format(wget_destination),hosts=all_hosts,
           connection_params={'user': 'root'}).run() ## move hadoop to a directory without the version
    ## CREATE THE MASTER FILE
    with open("hadoop-resources/tmp/master",'w') as f:
        f.write(list(masternode)[0] + "\n")
    Put(hosts=masternode,local_files=["hadoop-resources/tmp/master"],remote_location=hadoop_conf + "/master",
        connection_params={'user': 'root'}).run()
    ## CREATE THE SLAVES FILE
    with open("hadoop-resources/tmp/slaves","w") as f:
        for node in nodemanagers:
            f.write(node + "\n")
    Put(hosts=masternode,local_files=["hadoop-resources/tmp/slaves"],remote_location=hadoop_conf + "/slaves",
        connection_params={'user': 'root'}).run()
    ## CORE_SITE.XML
    replace_infile(pathin=path_core_site_template,pathout=path_core_site_tmp,replacements={"@namenode@":list(masternode)[0]})
    Put(hosts=all_hosts,local_files=[path_core_site_tmp],remote_location=hadoop_conf + "/core-site.xml",
        connection_params={'user': 'root'}).run() ## we upload core_site.xml to all hosts
    ## YARN_SITE.XML
    for host in all_hosts:
        nm_memory = (nodesDF.loc[nodesDF["node_name"]==host].RAM.values[0] - osMemory) * 1024 # multiply by 1024 .in nodesDF the RAM is in gigabytes
        replace_infile(pathin=path_yarn_site_template,pathout=path_yarn_site_tmp + host,
                       replacements={"@jobtracker@":list(masternode)[0],"@nodemanagermemory@":str(nm_memory)})
    Put(hosts=all_hosts,local_files=[path_yarn_site_tmp + "{{{host}}}"],remote_location=hadoop_conf + "/yarn-site.xml",
        connection_params={'user': 'root'}).run()
    ## MAP_RED.XML
    Put(hosts=all_hosts,local_files=[path_mapred_site_template],remote_location=hadoop_conf + "/mapred-site.xml",
        connection_params={'user': 'root'}).run()
    ### CHANGE THE JAVA_HOME ENVIRONMENTAL VARIABLE FOR HADOOP
    Remote("perl -pi -e 's,.*JAVA_HOME.*,export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre,g' {0}/hadoop-env.sh".format(hadoop_conf),
           hosts=all_hosts,connection_params={'user': 'root'}).run()
    ### WE GIVE PERMISSIONS TO THE G5K USER
    Remote("chown -R {0}:users /opt/hadoop*".format(g5k_configuration.get("g5k_user")),hosts=all_hosts,
           connection_params={'user': 'root'}).run()

def start_hadoop(nodesDF,masternode,nodemanagers,datanodes):
    all_hosts = nodesDF.node_name.tolist()
    hadoop_sbin = "/opt/hadoop/sbin"
    hadoop_bin = "/opt/hadoop/bin" ## This should be internal variables of the hadoop_util
    Remote("{0}/hadoop namenode -format".format(hadoop_bin),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()
    Remote("{0}/hadoop-daemon.sh --script hdfs start namenode".format(hadoop_sbin),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()
    Remote("{0}/yarn-daemon.sh start resourcemanager".format(hadoop_sbin),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()
    Remote("{0}/mr-jobhistory-daemon.sh start historyserver".format(hadoop_sbin),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()
    Remote("{0}/yarn-daemon.sh start nodemanager".format(hadoop_sbin),hosts=nodemanagers,connection_params={'user': g5k_configuration.get("g5k_user")}).run()
    Remote("{0}/hadoop-daemon.sh --script hdfs start datanode".format(hadoop_sbin),hosts=datanodes,connection_params={'user': g5k_configuration.get("g5k_user")}).run()

def delete_hadoop(path,masternode):
    Remote("/opt/hadoop/bin/hdfs dfs -rm -r {0}".format(path),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()

def create_hadoop_directory(path,masternode):
    Remote("/opt/hadoop/bin/hdfs dfs -mkdir {0}".format(path),hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()









