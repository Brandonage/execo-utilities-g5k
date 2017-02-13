from general_util import *


class NodesSpecificationError(Exception):
    def __init__(self,message):
        super(NodesSpecificationError,self).__init__("Wrong specification for nodes: {0}".format(message))
        self.message = message

wget_destination = "/opt"  ## This is the folder where we will download the wget files

##
##CURRENT LOGIC IS: IF COLOCATED, MAKE THE MASTER THE ONE WITH THE LEAST AMOUNT OF RAM, THE NODEMANAGERS THE N NODES WITH THE MOST AMMOUNT OF RAM AND THE DATANODES THE ONES WITH THE MOST STORAGE
##                  IF NOT COLOCATED, MAKE THE MASTER THE ONE WITH THE LEAST AMOUNT OF RAM, THE DATANODES THE ONES WITH THE MOST STORAGE AND THE ONES THAT ARE NOT MASTER NEITHER DATANODES AS NODEMANAGERS
def split_hadoop_roles(nodesDF,nDatanodes,nNodemanagers,colocated):
    if colocated:
        if (nNodemanagers>len(nodesDF)-1):
            raise NodesSpecificationError("Colocated: Number of nodemanagers greater than the number of nodes minus master node")
        if (nDatanodes>len(nodesDF)):
            raise NodesSpecificationError("Colocated: Number of datanodes greater than the number of nodes")
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
        if (nNodemanagers+nDatanodes>len(nodesDF)):
            raise NodesSpecificationError("Not Colocated: Number of nodemanagers plus datanodes greater than the number of nodes")
        master = node_with_smaller_memory(nodesDF) # The node with the smaller memory is the master
        nodemanagers = nodes_with_largest_memory(nodesDF[nodesDF["node_name"]!=list(master)[0]],nNodes=nNodemanagers) # the nodes that are not the master ((nodesDF[nodesDF["node_name"]!=list(master)[0]) are nodemanagers
        datanodes = nodes_with_largest_storage(nodesDF[~nodesDF["node_name"].isin(list(nodemanagers))],nNodes=nDatanodes)  # The first n nodes with more storage space are datanodes
    return datanodes, nodemanagers, master

### (nodes: DF with all the nodes in the reservation, datanodes, nodemanagers, master: An iterable with the name of the nodes, osMemory: the ammount of memory we want to leave free for OS)
def install_hadoop(nodesDF,masternode,osMemory): ##TODO remove {user:root} parameters since we changed them already on .execo.conf.py
    all_hosts = nodesDF.node_name.tolist()
    tarball_url = "http://www.eu.apache.org/dist/hadoop/common/hadoop-2.6.0/hadoop-2.6.0.tar.gz" ## whatever version we want
    path_core_site = "hadoop-resources/core-site.xml"
    path_yarn_site = "hadoop-resources/yarn-site.xml"
    path_mapred_site = "hadoop-resources/mapred-site.xml"
    hadoop_home = "/opt/hadoop" ## The directory where we are going to install hadoop in g5k
    hadoop_conf = hadoop_home + "/etc/hadoop/"
    Remote("mkdir -p " + hadoop_home,hosts=all_hosts,connection_params= {'user': 'root'}).run() ## we create the directories
    Remote("wget {url} -O {destination}/hadoop.tar.gz 2>1".format(url=tarball_url,destination=wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## Download the hadoop distribution on it
    Remote("cd {0} && tar -xvzf hadoop.tar.gz".format(wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## untar Hadoop
    Remote("cd {0} && mv hadoop-* hadoop".format(wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## untar Hadoop
    ## CORE_SITE.XML
    replace_infile(pathin=path_core_site + ".template",pathout=path_core_site,replacements={"@namenode@":list(masternode)[0]})
    Put(hosts=all_hosts,local_files=path_core_site,remote_location=hadoop_conf + "core-site.xml") ## we upload core_site.xml to all hosts
    ## YARN_SITE.XML
    for host in all_hosts:
        nm_memory = nodesDF.loc[nodesDF["node_name"]==host].RAM.values[0] - osMemory
        replace_infile(pathin=path_yarn_site + ".template",pathout=path_yarn_site + host,replacements={"@jobtracker@":list(masternode)[0],"@nodemanagermemory@":str(nm_memory)})
    Put(hosts=all_hosts,local_files=[path_yarn_site + host for host in all_hosts],remote_location=hadoop_conf + "yarn-site.xml").run()
    ## MAP_RED.XML
    Put(hosts=all_hosts,local_files=path_mapred_site + ".template",remote_location=hadoop_conf + "mapred-site.xml").run()
    ### CHANGE THE JAVA_HOME ENVIRONMENTAL VARIABLE FOR HADOOP
    Remote("perl -pi -e 's,.*JAVA_HOME.*,export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre,g' {0}/hadoop-env.sh".format(hadoop_conf),hosts=all_hosts,connection_params={'user': 'root'})






