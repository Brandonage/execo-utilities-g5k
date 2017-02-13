import hadoop_util
import general_util
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
        #general_util.install_JDK_7(self.nodes)
        self.datanodes_list, self.nodemanagers_list, self.masternode = hadoop_util.split_hadoop_roles(self.nodesDF,self.nDatanodes,self.nNodemanagers,self.colocated)
        hadoop_util.install_hadoop(self.nodesDF,self.masternode,self.os_memory)








