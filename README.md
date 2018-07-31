# execo-utilities-g5k

An easy way to script reproducible experiments on the g5k testbed. It uses a series of python classes to deploy
experiments in an easy, scripted way that facilitate the reservation of nodes in G5K, the deployment, the execution of
the experiment and the preservation of the results. There are several classes available to deploy experiments in the folder
experiments. You can think about this classes as laboratory notebooks that describe what your experiment looks like. 

To make it work we need to add in the in the .execo.conf.py file of our home directory the following key which will
be merged with the default execo.config.g5k_configuration

g5k_configuration = {
    'g5k_user' : 'abrandon'
}

It also needs the jsonpath_rw package

pip install --user jsonpath_rw

##Deploying experiments

### Oar Submission

The class responsible of running an experiment through an OAR reservation (https://www.grid5000.fr/mediawiki/index.php/Advanced_OAR) 
is OARExperiment. It has five main functions:
- reserve_nodes(): It reserves the nodes in G5K
- deploy_nodes(): If there are resources available after reserving, it deploys the machines on the resources
- install(): Users have to override this method to install on the machines everything needed for their experiments. The
class SparkOARExperiment is one example.
- run(): Also to be overrided, it has to contain all the instructions needed to run the experiment
- save_results(): It downloads to local the results of the experiments. In its more basic form it downloads information
about the machines used during the experiment with their specifications (RAM, CPU, etc.)

The file template.py can be used as a blueprint of what an experiment looks like. It reserves three nodes from the
graphene cluster for 2:25:00 and runs all the applications in SparkBench (https://github.com/CODAIT/spark-bench).

1. First, we create all the attributes of the experiment, namely, cluster and machines needed, walltime, date,
experiment name, frontend of the cluster we are going to use and a small description of the experiment

```python    dict = {"cluster":[("graphene",3)]}
    walltime = "2:25:00"
    date=None
    experiment_name="spark_benchmark_test"
    frontend="nancy"
    description="We want to experiment with Mesos and the building a framework with it"
```

2. We customise our OAR experiment by implementing the run function and we create the object for that experiment class
(note here how we use one of the benchmarks of the project https://github.com/Brandonage/execo-g5k-benchmarks).

```python class SparkExperimentTestBenchmark(SparkOARExperiment):
    def run(self):
        sb = SparkBench(home_directory="/home/abrandon/execo-g5k-benchmarks/spark/spark-bench/", master_node=spark_experiment.masternode,
                    resource_manager="yarn",root_to_spark_submit="/opt/spark/bin/spark-submit",default_master="yarn")
        sb.create_all_bench_files(prefix="_first",size=10,npartitions=40,conf=[["spark.executor.memory","7g"]])
        sb.launch_all_apps(prefix="_first",conf=[["spark.executor.memory","5g"]])
   
    spark_experiment = SparkExperimentTestBenchmark(frontend=frontend,resources=dict,walltime=walltime,
                            date=date,experiment_name=experiment_name,description=description,ndatanodes=3,nnodemanagers=2,colocated=True,os_memory=2) 
```

3. Reserve the nodes:

```python
spark_experiment.reserve_nodes()
```

4. Deploy nodes:

```python
spark_experiment.deploy_nodes()
```

5. Install all the required software needed for the experiment (monitoring tools, databases, dependencies, etc.). 
In this example, SparkExperimentTestBenchmark is a subclass of the SparkOARExperiment class, which installs JDK,
hadoop, spark and some monitoring tools in order to register the resource usage of Spark while executing the benchmark.
```python
spark_experiment.install()
```

6. Run the experiment (As shown in point 2 we overrided the run method to execute all the applications in the Spark Benchmark)
```python
spark_experiment.run()
```

7. Save the results. By default they are saved in $HOME/execo_experiments/ folder 

```python
spark_experiment.save_results()
```

8. Clean job

```python
spark_experiment.clean_job()
```

### Vagrant Submission

Another option is to deploy your experiment through virtual machines (VM's) that are spinned up through the vagrant-g5k tool of G5K.
The advantage is that you won't depend on specific clusters to be available as the VM's are started in whatever resources
available in G5K. It also allows you to have a set of homogeneous machines with the same specifications (RAM, CPU)

#### Prerequisites

- Vagrant-g5k installed (https://github.com/msimonin/vagrant-g5k)
- We assume vagrant-g5k is installed in $HOME/vagrant-g5k

The class responsible of running an experiment through a Vagrant reservation (https://www.grid5000.fr/mediawiki/index.php/Advanced_OAR) 
is VagrantExperiment. It has the same main five functions as OAR. In myexamples folder we can find an example named template_vagrant.py. 
In this case it uses the RcaVagrantExperiment class which in this concrete example we use to install a DCOS cluster on the VM's.

1. Reserve the nodes in G5K through vagrant-g5k before starting the script or launching the instructions on the Python console 
(https://github.com/msimonin/vagrant-g5k#usage). 
2.  Specify the number of resources needed. In contrast to the OAR method we use a list of three-tuples in which the format is
(number of machines,number of cores, RAM). Example for seven machines with 4 cores and 10GB of RAM
```python
dict = [(7, 4, 10)]
```

3. Create the object for that experiment class:

```python
vagrantrca_deployment = RcaVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                 experiment_name=experiment_name, description=description, nmasters=1,
                                                 nprivate_agents=4, npublic_agents=1)
```

4. Execute the reserve_nodes and deploy_nodes calls of the object (currently reserve_nodes is not implemented since this 
is done throught the vagrant up command launched in point 1)

```python
vagrantrca_deployment.reserve_nodes()
vagrantrca_deployment.deploy_nodes()
```

5. In this case we execute one of the methods of RcaVagrantExperiment which splits the roles of the different machines in order
to install DCOS.

```python
vagrantrca_deployment.split_dcos_roles()
```

6. We install DCOS and other tools needed

```python
vagrantrca_deployment.install()
```

7. Run the experiment

```python
vagrantrca_deployment.run()
```

8. Save the results
```python
vagrantrca_deployment.save_results()
```

##Bugs or problems

Please open an issue or contact me directly and I can help you to set everything up 



