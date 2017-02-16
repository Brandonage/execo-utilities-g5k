import hadoop_util
import spark_util
import monitoring_util
import mongodb_util
from experiment import *
###TODO TO BE INCLUDED IN A SEPARATE MODULE WITH ALL THE TYPES OF EXPERIMENTS WE CAN HAVE. A FACTORY OF EXPERIMENTS WILL CREATE DIFFERENT TYPES OF EXPERIMENTS E.G (SPARK,FLINK,MAPREDUCE...)

# (frontend: String, resources: dict of resources we want to reserve, walltime : HH:MM:SS, date : when to start experiment,
# experiment_name : String, datanodes: Int, nodemanager: Int, colocated:boolean, OS_memory : Int )
class SparkExperiment(Experiment):
    datanodes_list = None
    nodemanagers_list = None
    masternode = None
    ##TODO Topology of the cluster (Maybe not needed, the nodes are enough for it. Although it will be nice to have a description of the cluster, (e.g memory on each node and the CPU's and so on)
    def __init__(self,frontend,resources,walltime,date,experiment_name,nDatanodes,nNodemanagers,colocated,os_memory):
        Experiment.__init__(self,frontend,resources,walltime,date,experiment_name)
        self.nDatanodes = nDatanodes
        self.nNodemanagers = nNodemanagers
        self.colocated = colocated
        self.os_memory = os_memory

    def install(self): ## install all the necessary things for an Spark Experiment
        general_util.update_apt(self.nodes)
        general_util.install_JDK_7(self.nodes)
        self.datanodes_list, self.nodemanagers_list, self.masternode = hadoop_util.split_hadoop_roles(self.nodesDF,self.nDatanodes,self.nNodemanagers,self.colocated)
        hadoop_util.install_hadoop(self.nodesDF,self.masternode,self.datanodes_list,self.os_memory)
        spark_util.install_spark(self.nodesDF,self.nodemanagers_list,self.masternode)
        hadoop_util.start_hadoop(self.nodesDF,self.masternode,self.nodemanagers_list,self.datanodes_list)
        general_util.install_dstat(self.nodes)
        mongodb_util.install_and_run_mongodb(self.masternode)
        monitoring_util.install_gmone(master=self.masternode, slaves=self.nodemanagers_list)
        monitoring_util.start_gmone(master=self.masternode,slaves=self.nodemanagers_list)

    def describe_cluster(self):
        print ("Master node is: " + str(list(self.masternode)))
        print ("Nodemanagers are: " + str(list(self.nodemanagers_list)))
        print ("Datanodes are: " + str(list(self.datanodes_list)))
        print ("All nodes are: " + str(list(self.nodes)))
        print (self.nodesDF)









