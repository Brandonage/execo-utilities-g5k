from spark_experiment import *
import sys
## TODO: Install it in PYTHON environment variable so you can import directly
sys.path.extend(["/Users/alvarobrandon/PycharmProjects/execo_g5k_benchmarks/spark"])
from sparkbench import SparkBench



if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = {"cluster":[("grimoire",1),("grisou",1),("graphene",3)]}
    walltime = "2:25:00"
    date=None
    experiment_name="execo_test"
    frontend="nancy"
    spark_experiment = SparkExperiment("nancy",resources=dict,walltime=walltime,
                            date=None,experiment_name=experiment_name,nDatanodes=5,nNodemanagers=4,colocated=True,os_memory=2)
    spark_experiment.reserve_nodes()
    spark_experiment.deploy_nodes()
    spark_experiment.install()
    spark_experiment.clean_job()
    sb = SparkBench(home_directory="/home/abrandon/spark-bench/", master_node=spark_experiment.masternode,
                    resource_manager="yarn",root_to_spark_submit="/opt/spark/bin/spark-submit",default_master="yarn")
    sb.launchgenerategraphfile(output="graphs",size=30,npartitions="100",submit_conf=[["spark.executor.memory","7g"]],scheduler_options="")