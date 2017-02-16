from general_util import *



def install_spark(nodesDF,nodemanagers,masternode):
    all_hosts = nodesDF.node_name.tolist()
    tarball_url = "http://www.eu.apache.org/dist/spark/spark-1.6.2/spark-1.6.2-bin-hadoop2.6.tgz" ## whatever version we want
    spark_home = "/opt/spark" ## The directory where we are going to install hadoop in g5k
    spark_conf = spark_home + "/conf"
    ## We get, untar and prepare the directory for Spark
    Remote("wget {url} -O {destination}/spark.tar.gz 2>1".format(url=tarball_url,destination=wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## Download the hadoop distribution on it
    Remote("cd {0} && tar -xvzf spark.tar.gz".format(wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## untar Spark
    Remote("cd {0} && mv spark-* spark".format(wget_destination),hosts=all_hosts,connection_params={'user': 'root'}).run() ## move Spark to a new directory without the version name
    ## CREATE THE MASTER FILE
    with open("spark-resources/master",'w') as f:
        f.write(list(masternode)[0] + "\n")
    Put(hosts=masternode,local_files=["spark-resources/master"],remote_location=spark_conf + "/master").run()
    ## CREATE THE SLAVES FILE
    with open("spark-resources/slaves","w") as f:
        for node in nodemanagers:
            f.write(node + "\n")
    Put(hosts=masternode,local_files=["spark-resources/slaves"],remote_location=spark_conf + "/slaves").run()
    #### WE PUT TWO ADDITIONAL FILES: spark-defaults.conf and spark-env.sh
    replace_infile(pathin="spark-resources/spark-defaults.conf.template",pathout="spark-resources/spark-defaults.conf",replacements={"@jobtracker@":list(masternode)[0]})
    Put(hosts=all_hosts,local_files=["spark-resources/spark-defaults.conf"],remote_location=spark_conf + "/spark-defaults.conf").run()
    Put(hosts=all_hosts,local_files=["spark-resources/spark-env.sh"],remote_location=spark_conf + "/spark-env.sh").run()
    ### WE GIVE PERMISSIONS TO THE G5K USER
    Remote("chown -R {0}:users /opt/spark*".format(g5k_configuration.get("g5k_user")),hosts=all_hosts,connection_params={'user': 'root'}).run()

def start_spark(nodesDF,masternode,nodemanagers):
    pass

def start_history_server(masternode):
    Remote("/opt/spark/sbin/start-history-server.sh",hosts=masternode,connection_params={'user': g5k_configuration.get("g5k_user")}).run()

def prepare_dynamic_allocation(nodemanagers):
    Remote("cp /opt/spark/lib/spark-*-yarn-shuffle.jar /opt/hadoop/share/hadoop/yarn",hosts=nodemanagers,connection_params={'user': g5k_configuration.get("g5k_user")}).run()