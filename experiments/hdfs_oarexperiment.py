from oarexperiment import OARExperiment
from utils import general_util, spark_util, hadoop_util


###TODO TO BE INCLUDED IN A SEPARATE MODULE WITH ALL THE TYPES OF EXPERIMENTS WE CAN HAVE. A FACTORY OF EXPERIMENTS WILL
#  CREATE DIFFERENT TYPES OF EXPERIMENTS E.G (SPARK,FLINK,MAPREDUCE...).

# (frontend: String, resources: dict of resources we want to reserve, walltime : HH:MM:SS, date : when to start experiment,
# experiment_name : String, datanodes: Int, nodemanager: Int, colocated:boolean, OS_memory : Int )
## This is in fact a template object that we can copy to create new experiments overriding the run part
class HdfsOARExperiment(OARExperiment):
    datanodes_list = None
    nodemanagers_list = None
    masternode = None

    ##TODO Topology of the cluster (Maybe not needed, the nodes are enough for it. Although it will be nice to have a description of the cluster, (e.g memory on each node and the CPU's and so on)
    def __init__(self, frontend, resources, walltime, date, experiment_name,description, ndatanodes, nnodemanagers, colocated,
                 os_memory):
        OARExperiment.__init__(self, frontend, resources, walltime, date, experiment_name, description)
        self.ndatanodes = ndatanodes
        self.nnodemanagers = nnodemanagers
        self.colocated = colocated
        self.os_memory = os_memory


    def install(self):  ## install all the necessary things for an Spark OARExperiment
        # before starting the installation process, let's check if the deployed nodes are sufficient for the specified roles
        hadoop_util.validate_cluster_parameters(self.nodes, self.ndatanodes, self.nnodemanagers, self.colocated)
        # prepare the JDK
        general_util.install_general_utils(self.nodes)
        general_util.update_apt(self.nodes)
        general_util.install_JDK_8(self.nodes)
        # start with the hadoop installation:
        # 1. prepare the roles
        self.datanodes_list, self.nodemanagers_list, self.masternode = hadoop_util.split_hadoop_roles(self.nodesDF,
                                                                                                      self.ndatanodes,
                                                                                                      self.nnodemanagers,
                                                                                                      self.colocated)
        # 2. install the files needed
        hadoop_util.install_hadoop(self.nodesDF, self.masternode, self.datanodes_list, self.os_memory, source=None)
        # start the spark installation
        spark_util.install_spark(master=self.masternode, slaves=self.nodemanagers_list, monitor=False, source="2.0.1")
        # prepare the files for dynamic allocation. This copies spark-*-yarn-shuffle.jar to the share yarn directory
        spark_util.prepare_dynamic_allocation(nodemanagers=self.nodemanagers_list)
        # launch hadoop daemons
        hadoop_util.start_hadoop(self.masternode, self.nodemanagers_list, self.datanodes_list)
        spark_util.start_history_server(masternode=self.masternode)

    ## we will override this part to implement the experiment that we want
    def run(self):
        pass

    # save the results of the experiment
    def save_results(self):
        pass

    # prints the cluster descpription
    def describe_cluster(self):
        print self.spark_cluster_description()

    # From here we find the methods that belong to the SparkOARExperiment class
    #
    # A description of the cluster
    def spark_cluster_description(self):
        """

        :rtype: str
        """
        result = "Master node is: " + str(list(self.masternode)) + '\n' + "Nodemanagers are: " + str(
            list(self.nodemanagers_list)) + '\n' + \
              "Datanodes are: " + str(list(self.datanodes_list)) + '\n' + \
              "All nodes are: " + str(list(self.nodes)) + '\n' + \
              self.nodesDF.to_string()
        return result
