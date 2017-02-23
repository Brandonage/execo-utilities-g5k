### THIS IS THE SCRIPT WE ARE GOING TO EXECUTE IN THE GRID5000 FRONTEND AND THE TEMPLATE FOR OUR EXPERIMENTS

import sys
#   we add the paths in the frontend to be able to import SparkBench and the Experiment classes
## TODO: Install it in PYTHON environment variable so you can import directly.
sys.path.extend(["/home/abrandon/execo_g5k_benchmarks/spark"])
sys.path.extend(["/home/abrandon/execo_utilities_g5k"])
from sparkbench import SparkBench
from spark_experiment import *

class SparkExperimentTestBenchmark(SparkExperiment):

    def run(self):
        sb = SparkBench(home_directory="/home/abrandon/spark-bench/", master_node=spark_experiment.masternode,
                    resource_manager="yarn",root_to_spark_submit="/opt/spark/bin/spark-submit",default_master="yarn")
        sb.create_all_bench_files(prefix="_first",size=10,npartitions=40,conf=[["spark.executor.memory","7g"]])
        sb.launch_all_apps(prefix="_first",conf=[["spark.executor.memory","5g"]])




if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = {"cluster":[("graphene",9)]}
    walltime = "4:25:00"
    date=None
    experiment_name="spark_benchmark_test"
    frontend="nancy"
    description="A simple reproducible experiment with execo that executes all the applications from the SparkBenchmark:" \
                " with a file size of 10 and 40 partitions"
    spark_experiment = SparkExperimentTestBenchmark("nancy",resources=dict,walltime=walltime,
                            date=date,experiment_name=experiment_name,description=description,ndatanodes=5,nnodemanagers=4,colocated=True,os_memory=2)
    # TODO: All of this instructions can be wrapped in a method like .start()
    spark_experiment.reserve_nodes()
    spark_experiment.deploy_nodes()
    spark_experiment.install()
    spark_experiment.run()
    spark_experiment.save_results()
    spark_experiment.clean_job()
