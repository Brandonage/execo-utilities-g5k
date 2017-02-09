from submission import *
###TODO TO BE INCLUDED IN A SEPARATE MODULE WITH ALL THE TYPES OF EXPERIMENTS WE CAN HAVE. A FACTORY OF EXPERIMENTS WILL CREATE DIFFERENT TYPES OF EXPERIMENTS E.G (SPARK,FLINK,MAPREDUCE...)

# (frontend: String, resources: dict of resources we want to reserve, walltime : HH:MM:SS, date : when to start experiment,
# experiment_name : String, datanodes: Int, nodemanager: Int, colocated:boolean, OS_memory : Int )
class SparkExperiment:
    jobid = 0  ## The jobid that is linked to this experiment
    nodes = None  ## The nodes that form part of this reservation
    datanodes_list = None
    nodemanagers_list = None
    masternode = None
    ##TODO Topology of the cluster (Maybe not needed, the nodes are enough for it. Although it will be nice to have a description of the cluster, (e.g memory on each node and the CPU's and so on)
    def __init__(self,frontend,resources,walltime,date,experiment_name,nDatanodes,nNodemanagers,colocated,os_memory):
        self.frontend = frontend
        self.resources = resources
        self.walltime = walltime
        self.data = date
        self.experiment_name = experiment_name
        self.nDatanodes = nDatanodes
        self.nNodemanagers = nNodemanagers
        self.colocated = colocated
        self.os_memory = os_memory
        pass

    def reserve_nodes(self):
        self.jobid = reserve_nodes(self.frontend,self.resources,self.walltime,self.date,self.experiment_name)

    def deploy_nodes(self):
        deployed, undeployed = deploy_nodes(self.frontend,self.jobid)
        if len(undeployed)>0:
            print ("There are undeployed nodes")
        else:
            print ("All nodes deployed")
        self.nodes = deployed

    def install_yarn_and_hdfs(self):
        self.datanodes_list, self.nodemanagers_list, self.masternode = install_hdfs(self.nodes,self.nDatanodes,self.nNodemanagers,self.colocated)



