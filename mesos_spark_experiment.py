from experiment import *
import mesos_util
from spark_experiment import SparkExperiment

###TODO TO BE INCLUDED IN A SEPARATE MODULE WITH ALL THE TYPES OF EXPERIMENTS WE CAN HAVE. A FACTORY OF EXPERIMENTS WILL CREATE DIFFERENT TYPES OF EXPERIMENTS E.G (SPARK,FLINK,MAPREDUCE...)

# (frontend: String, resources: dict of resources we want to reserve, walltime : HH:MM:SS, date : when to start experiment,
# experiment_name : String, datanodes: Int, nodemanager: Int, colocated:boolean, OS_memory : Int )
## This is in fact a template object that we can copy to create new experiments overriding the run part
class MesosSparkExperiment(SparkExperiment):

    master_list = None
    ## The attributes we need are basically the same as an SparkExperiment with Hadoop but we can have several masters

    def __init__(self, frontend, resources, walltime, date, experiment_name,description, ndatanodes, nnodemanagers, colocated,
                 os_memory,nmasters):
        SparkExperiment.__init__(self, frontend, resources, walltime, date, experiment_name, description,
                                 ndatanodes,nnodemanagers,colocated,os_memory)
        self.nmasters = nmasters


    def install(self):  ## install all the necessary things for an Spark Experiment
        SparkExperiment.install(self) # we do all the installations as the parent class
#        mesos_util.build_and_install_mesos(self.masternode.union(self.nodemanagers_list))
        #   We will configure mesos with only the master node as the list of master nodes
        if self.nmasters == 1:
            self.master_list = self.masternode
#        mesos_util.configure_mesos(self.masternode,self.master_list,self.nodemanagers_list,self.os_memory)
        #mesos_util.start_mesos(self.masternode)

    ## we will override this part to implement the experiment that we want
    def run(self):
        pass

    # save the results of the experiment
    def save_results(self):
        SparkExperiment.save_results(self)

    # prints the cluster descpription
    def describe_cluster(self):
        SparkExperiment.describe_cluster(self)

    # From here we find the methods that belong to the SparkExperiment class
    #
    # A description of the cluster


