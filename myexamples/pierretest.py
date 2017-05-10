### THIS IS THE SCRIPT WE ARE GOING TO EXECUTE IN THE GRID5000 FRONTEND AND THE TEMPLATE FOR OUR EXPERIMENTS
### THIS SCRIPTS WILL BE PLACE INSIDE THE EXECO_UTILITIES_G5K root directory, possibly in a experiments folder and executed like py experiments/script.py
import sys
#   we add the paths in the frontend to be able to import SparkBench and the OARExperiment classes
## TODO: Add the paths in PYTHON environment variable so you can import directly.
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks/spark"])
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
from sparkbench import SparkBench
from experiments.hdfs_oarexperiment import HdfsOARExperiment


class SparkExperimentTestBenchmark(HdfsOARExperiment):
    def run(self):  ## remember to set the home_directory variable to the sparkbenchmark root directory
        sb = SparkBench(home_directory="/home/abrandon/execo-g5k-benchmarks/spark/spark-bench/", master_node=spark_experiment.masternode,
                    resource_manager="yarn",root_to_spark_submit="/opt/spark/bin/spark-submit",default_master="yarn")
        sb.launchgeneratetextfile(output="words.txt", size=60,npartitions=200,submit_conf=[["spark.executor.memory","7g"]])
        sb.launchgeneratedectreefile(output="dec.txt", size=60,npartitions=200,submit_conf=[["spark.executor.memory","7g"]])
        # sb.launchgenerategraphfile(output="graph.txt", size=12,npartitions=40,submit_conf=[["spark.executor.memory","7g"]])
        # sb.launchsort(input="words.txt",submit_conf=[["spark.executor.memory","4g"]])
        # sb.launchgrep(input="words.txt",submit_conf=[["spark.executor.memory","4g"]])
        sb.launchngrams(input="words.txt",submit_conf=[["spark.executor.memory","4g"]])
        sb.launchdecisiontrees(input="dec.txt",submit_conf=[["spark.executor.memory","4g"]])
        # sb.launchconnectedcomponent(input="graph.txt",submit_conf=[["spark.executor.memory","7g"]])




if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = {"cluster":[("paravance",5)]}
    walltime = "2:25:00"
    date=None
    experiment_name="spark_benchmark_2.0_test"
    frontend="rennes"
    description="OARExperiment to evaluate the convergence between HPC and cloud"
    spark_experiment = SparkExperimentTestBenchmark(frontend=frontend,resources=dict,walltime=walltime,
                            date=date,experiment_name=experiment_name,description=description,ndatanodes=5,nnodemanagers=4,colocated=True,os_memory=2)
    # TODO: Change the hadoop_util.validate_cluster_parameters
    spark_experiment.reserve_nodes()
    spark_experiment.deploy_nodes()
    spark_experiment.install()
    spark_experiment.run()
    spark_experiment.save_results()
    spark_experiment.clean_job()
