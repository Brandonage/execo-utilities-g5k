import sys
# We extend the paths in case we want to upload the experiment to G5K frontend
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks"])
from experiments.fmone_vagrantexperiment import FmoneVagrantExperiment
from time import sleep
from glob import glob
import pandas as pd
from sklearn import preprocessing





if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(60,4,10)] # the format is nnodes,cores,GB
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="nancy"
    description="This experiment evaluates the elasticity of Fmone"
    vagrantdcos_deployment = FmoneVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                    experiment_name=experiment_name, description=description, nmasters=3,
                                                    nprivate_agents=55, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.split_dcos_roles()
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.upload_frontends()
    vagrantdcos_deployment = FmoneVagrantExperiment.reload_experiment()
    vagrantdcos_deployment.reload_keys() # If we upload to the frontends we have to reload the keys
    vagrantdcos_deployment.install()
    # I build the regions and I leave an ncentral number of private node as the central region
    ncentral = 4
    # [8,22,39,33]
    vagrantdcos_deployment.build_regions(proportions=[8,22,39,33], central_region=set(list(vagrantdcos_deployment.private_agents)[-ncentral:]))
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    # Next, cassandra is going to be installed in the central region
    # ncassandra is not used since it is always installed in the central region
    vagrantdcos_deployment.install_cassandra(ncassandra=str(ncentral),nseeds="1")
    # We will install yscb in all the regions but the central one.
    regions_to_install = filter(lambda r: not r.issubset(vagrantdcos_deployment.central_region),
                                vagrantdcos_deployment.regions)
    nodes_to_install = set.union(*regions_to_install)
    vagrantdcos_deployment.ycsb_install_regions(nodes_to_install)
    workloads = ["workloada","workloadb","workloadc","workloadd","workloadf"]
    # We include here a comparison with Prometheus centralised approach
    vagrantdcos_deployment.start_cadvisor_containers()
    cadvisor_targets=map(lambda x : x + ':8082',list(vagrantdcos_deployment.nodes))
    vagrantdcos_deployment.start_prometheus_in_region(region=0,targets=cadvisor_targets,federated_targets=False)
    sleep(560)
    vagrantdcos_deployment.start_dummy_containers()
    vagrantdcos_deployment.add_delay(bandwidth="4Mbit",delay="50ms")
    vagrantdcos_deployment.ycsb_run(iterations=1,res_dir="prometheus",workloads=workloads, recordcount="1000",threadcount="1", fieldlength="500", target="40")
    vagrantdcos_deployment.stop_cadvisor_containers()
    vagrantdcos_deployment.stop_all_prometheus_instances()
    vagrantdcos_deployment.start_kafka_queue()
    vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="central_ycsb_kafka",
                                              slaves=str(vagrantdcos_deployment.private_agents.__len__()-1),
                                              region="0") # The region is not even used
    sleep(460)
    vagrantdcos_deployment.ycsb_run(iterations=1,res_dir = "central",workloads=workloads, recordcount="1000",threadcount="1", fieldlength="500", target="40")
    vagrantdcos_deployment.clean_marathon_groups()
    sleep(360)
    vagrantdcos_deployment.start_dummy_containers()
    i = 0
    for r in vagrantdcos_deployment.regions[:-1]: # all but the central region. Note that when the regions are built the central region is appended last
        vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="regional_mongo",
                                                  slaves=str(r.__len__()),
                                                  region=str(i))
        i=i+1

    sleep(380)
    vagrantdcos_deployment.ycsb_run(iterations=1,res_dir="regional",workloads=workloads, recordcount="1000",threadcount="1", fieldlength="500", target="40")
    vagrantdcos_deployment.clean_marathon_groups()
    sleep(360)
    vagrantdcos_deployment.start_dummy_containers()
    i = 0
    for r in vagrantdcos_deployment.regions[:-1]: # all but the central region
        vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="aggregate", # for the aggregate pipeline you have to start the mongocloud instance
                                                  slaves=str(r.__len__()),
                                                  region=str(i))
        i=i+1


    sleep(380)
    vagrantdcos_deployment.ycsb_run(iterations=1,res_dir="aggregate",workloads=workloads, recordcount="1000",threadcount="1", fieldlength="500", target="40")
    vagrantdcos_deployment.save_results()
    vagrantdcos_deployment.analyse_results(workloads)


    # Check the resource usage of the backend. We can try different backends but for now lets try the MongoDB backend. It is very resource efficient or so we think

    vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="central_ycsb",
                                              slaves=str(vagrantdcos_deployment.private_agents.__len__() - 1),
                                              region="0")  # The region is not even used


    #check the elasticity of the containers. How fast can they start with and without pulling the images
    slaves_and_region = [("1","regioncentral"),("2","region0"),("10","region1"),("30","region2")]
    force_pull = [True,False]
    results_elasticity = []
    for s in slaves_and_region:
        for f in force_pull:    # The check elasticity function checks needs the number of slaves the force_pull flag and the region
            results_elasticity.append(vagrantdcos_deployment.check_elasticity(s[0],f,s[1]))

    #deploy a pipeline to check its resilience
    vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="regional_mongo",
                                              slaves=str("15"), ## OJO AL NUMERO DE SLAVES
                                              region="2")
    results_resilience = []
    for i in xrange(5):
        results_resilience.append(vagrantdcos_deployment.check_resilience())
        # The check resilience function checks how much time it takes to start again the pipeline given that one agent fails,
        # one mongoDB instance fails and that the whole pipeline fails


    # Flexible backends and the resource usage.
    # With this experiment we want to proof that different monitoring backends have different resource usage
    # requirements. FMonE design is based on flexible backends, allowing the user to choose one depending on te capacity
    # of the underlying hardware.

    files_for_results = "/Users/alvarobrandon/execo_experiments/resource_usage_fmone/*.xls"
    kafka_results = []
    for f in glob(files_for_results):
        df = pd.read_excel(f)
        df[['usr', 'sys', 'idl']] = df[['usr', 'sys', 'idl']] / 1000
        df['used'] = df['used']/100000000
        if 'kafka' in f:
            kafka_results.append(df)
        if 'prom' in f:
            prom = df
        if 'mongodb' in f:
            mongodb = df
    kafka = pd.concat(kafka_results)
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0,100))
    min_max_scaler.fit(kafka['writ'].append(mongodb['writ']).append(prom['writ']))
    kafka['writ'] = min_max_scaler.transform(kafka['writ'])
    mongodb['writ'] = min_max_scaler.transform(mongodb['writ'])
    prom['writ'] = min_max_scaler.transform(prom['writ'])
    print "cpu_usr\tcpu_usr_std\tused\tused_std\twrit\twrit_std\n{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n{12}\t{13}\t{14}\t{15}\t{16}\t{17}".\
        format(kafka['usr'].mean(),kafka['usr'].std(),kafka['used'].mean(),kafka['used'].std(),kafka['writ'].mean(),kafka['writ'].std(),
               prom['usr'].mean(),prom['usr'].std(),prom['used'].mean(),prom['used'].std(),prom['writ'].mean(),prom['writ'].std(),
               mongodb['usr'].mean(),mongodb['usr'].std(),mongodb['used'].mean(),mongodb['used'].std(),mongodb['writ'].mean(),mongodb['writ'].std())


# DESCRIPTION OF YCSB WORKLOADS #

# The core workloads consist of six different workloads:
#
# Workload A: Update heavy workload
#
# This workload has a mix of 50/50 reads and writes. An application example is a session store recording recent actions.
#
# Workload B: Read mostly workload
# This workload has a 95/5 reads/write mix. Application example: photo tagging; add a tag is an update, but most operations are to read tags.
#
# Workload C: Read only
#
# This workload is 100% read. Application example: user profile cache, where profiles are constructed elsewhere (e.g., Hadoop).
#
# Workload D: Read latest workload
#
# In this workload, new records are inserted, and the most recently inserted records are the most popular. Application example: user status updates; people want to read the latest.
#
# Workload E: Short ranges
#
# In this workload, short ranges of records are queried, instead of individual records. Application example: threaded conversations, where each scan is for the posts in a given thread (assumed to be clustered by thread id).
#
# Workload F: Read-modify-write
# In this workload, the client will read a record, modify it, and write back the changes. Application example: user database, where user records are read and modified by the user or to record user activity.


