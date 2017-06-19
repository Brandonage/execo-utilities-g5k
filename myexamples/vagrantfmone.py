import sys
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks"])
from experiments.fmone_vagrantexperiment import FmoneVagrantExperiment
from time import sleep
from aux_utilities.twilio_client import create_twilio_client






if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(15,2,4)]
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="rennes"
    description="This is a deployment using vagrant_g5k and DCOS"
    vagrantdcos_deployment = FmoneVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                    experiment_name=experiment_name, description=description, nmasters=1,
                                                    nprivate_agents=12, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.split_dcos_roles()
    vagrantdcos_deployment.install()
    # I build the regions and I leave the last private node as the central region
    vagrantdcos_deployment.build_regions(proportions=[50, 50], central_region=set(list(vagrantdcos_deployment.private_agents)[-4:]))
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.upload_frontends()
    vagrantdcos_deployment = FmoneVagrantExperiment.reload_experiment()
    vagrantdcos_deployment.reload_keys() # If we upload to the frontends we have to reload the keys
    vagrantdcos_deployment.install_cassandra(ncassandra="4",nseeds="1")
    # TODO: All of this should go into the run procedure
    vagrantdcos_deployment.ycsb_install()
    # Stop here. You have to prepare the cassandra DB
    vagrantdcos_deployment.add_delay(bandwidth="3Mbit",delay="50ms")
    workloads = ["workloada","workloadc"]
    vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "no_fmone",workloads=workloads, recordcount="8000",threadcount="1", fieldlength="500", target="100")
    client, dest_phone, orig_phone = create_twilio_client()
    if client is not None:
        client.messages.create(to=dest_phone,from_=orig_phone,body="Starting the Fmone pipeline. Verify on DC/OS")
    vagrantdcos_deployment.run_fmone_pipeline()
    sleep(380)
    vagrantdcos_deployment.checkpoint_network()
    vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "with_fmone",workloads=workloads, recordcount="8000",threadcount="1", fieldlength="500", target="100")
    vagrantdcos_deployment.checkpoint_network()
    vagrantdcos_deployment.save_results()
    vagrantdcos_deployment.analyse_results(workloads)


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