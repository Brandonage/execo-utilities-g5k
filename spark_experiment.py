import hadoop_util
import spark_util
import monitoring_util
import mongodb_util
from experiment import *


###TODO TO BE INCLUDED IN A SEPARATE MODULE WITH ALL THE TYPES OF EXPERIMENTS WE CAN HAVE. A FACTORY OF EXPERIMENTS WILL
#  CREATE DIFFERENT TYPES OF EXPERIMENTS E.G (SPARK,FLINK,MAPREDUCE...).

# (frontend: String, resources: dict of resources we want to reserve, walltime : HH:MM:SS, date : when to start experiment,
# experiment_name : String, datanodes: Int, nodemanager: Int, colocated:boolean, OS_memory : Int )
## This is in fact a template object that we can copy to create new experiments overriding the run part
class SparkExperiment(Experiment):
    datanodes_list = None
    nodemanagers_list = None
    masternode = None

    ##TODO Topology of the cluster (Maybe not needed, the nodes are enough for it. Although it will be nice to have a description of the cluster, (e.g memory on each node and the CPU's and so on)
    def __init__(self, frontend, resources, walltime, date, experiment_name,description, ndatanodes, nnodemanagers, colocated,
                 os_memory):
        Experiment.__init__(self, frontend, resources, walltime, date, experiment_name, description)
        self.ndatanodes = ndatanodes
        self.nnodemanagers = nnodemanagers
        self.colocated = colocated
        self.os_memory = os_memory


    def install(self):  ## install all the necessary things for an Spark Experiment
        # before starting the installation process, let's check if the deployed nodes are sufficient for the specified roles
        hadoop_util.validate_cluster_parameters(self.nodes,self.ndatanodes,self.nnodemanagers,self.colocated)
        # prepare the JDK
        general_util.update_apt(self.nodes)
        general_util.install_JDK_8(self.nodes)
        # start with the hadoop installation:
        # 1. prepare the roles
        self.datanodes_list, self.nodemanagers_list, self.masternode = hadoop_util.split_hadoop_roles(self.nodesDF,
                                                                                                      self.ndatanodes,
                                                                                                      self.nnodemanagers,
                                                                                                      self.colocated)
        # 2. install the files needed
        hadoop_util.install_hadoop(self.nodesDF, self.masternode, self.datanodes_list, self.os_memory)
        # start the spark installation
        spark_util.install_spark(master=self.masternode, slaves=self.nodemanagers_list)
        # prepare the files for dynamic allocation. This copies spark-*-yarn-shuffle.jar to the share yarn directory
        spark_util.prepare_dynamic_allocation(nodemanagers=self.nodemanagers_list)
        # launch hadoop daemons
        hadoop_util.start_hadoop(self.nodesDF, self.masternode, self.nodemanagers_list, self.datanodes_list)
        spark_util.start_history_server(masternode=self.masternode)
        mongodb_util.install_and_run_mongodb(self.masternode)
        # install dstat (to be used by GMone)
        general_util.install_dstat(self.nodes)
        # install and start gmone
        monitoring_util.install_gmone(master=self.masternode, slaves=self.nodemanagers_list)
        monitoring_util.start_gmone(master=self.masternode, slaves=self.nodemanagers_list)
        # install and start slim
        monitoring_util.install_slim(master=self.masternode)
        monitoring_util.start_slim(master=self.masternode)

    ## we will override this part to implement the experiment that we want
    def run(self):
        pass

    # save the results of the experiment
    def save_results(self):
        Experiment.save_results(self)  # parent method common to all experiments
        with open("{0}/roles_description.txt".format(self.results_directory), "w") as text_file:
            text_file.write(self.spark_cluster_description()) # save all the roles of the hadoop cluster
        # create the directory where the mongo export files are going to be
        mongo_export_dir = self.results_directory + "/mongo_export"
        if not exists(mongo_export_dir):
            makedirs(mongo_export_dir)
        # export the mongo databases we have
        self.export_gmone_metrics(directory=mongo_export_dir)
        self.export_slim_metrics(directory=mongo_export_dir)
        # export the spark-events files for the UI
        spark_events_dir = self.results_directory + "/spark_events"
        if not exists(spark_events_dir):
            makedirs(spark_events_dir)
        self.export_spark_ui_metrics(directory=spark_events_dir)

    # prints the cluster descpription
    def describe_cluster(self):
        print self.spark_cluster_description()

    # From here we find the methods that belong to the SparkExperiment class
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

    def export_slim_metrics(self, directory):
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="apps",
                                    out_path=directory + "/apps.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="environment",
                                    out_path=directory + "/environment.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="executors",
                                    out_path=directory + "/executors.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="jobs",
                                    out_path=directory + "/jobs.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="non_rdd_blocks",
                                    out_path=directory + "/non_rdd_blocks.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="rdd_blocks",
                                    out_path=directory + "/rdd_blocks.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="rdd_executors",
                                    out_path=directory + "/rdd_executors.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="rdds",
                                    out_path=directory + "/rdds.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="stage_attempts",
                                    out_path=directory + "/stage_attempts.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="stage_executors",
                                    out_path=directory + "/stage_executors.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="stage_summary_metrics",
                                    out_path=directory + "/stage_summary_metrics.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="stages",
                                    out_path=directory + "/stages.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="task_attempts",
                                    out_path=directory + "/task_attempts.json")
        mongodb_util.export_mongodb(node=self.masternode, database="meteor", collection="tasks",
                                    out_path=directory + "/tasks.json")

    def export_gmone_metrics(self, directory):
        mongodb_util.export_mongodb(node=self.masternode, database="gmone", collection="readings",
                                    out_path=directory + "/readings.json")

    def export_spark_ui_metrics(self, directory):
        spark_util.export_spark_events(node=self.masternode, out_dir=directory)
