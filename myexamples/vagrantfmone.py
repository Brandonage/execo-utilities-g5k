import sys
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks"])
from experiments.fmone_vagrantexperiment import FmoneVagrantExperiment
from time import sleep
from aux_utilities.twilio_client import create_twilio_client






if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(10,2,4)]
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="rennes"
    description="This is a deployment using vagrant_g5k and DCOS"
    vagrantdcos_deployment = FmoneVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                    experiment_name=experiment_name, description=description, nmasters=1,
                                                    nprivate_agents=7, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.split_dcos_roles()
    vagrantdcos_deployment.install()
    # I build the regions and I leave the last private node as the central region
    vagrantdcos_deployment.build_regions(proportions=[50, 50], central_region=set(list(vagrantdcos_deployment.private_agents)[-2:]))
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.upload_frontends()
    vagrantdcos_deployment.reload_keys() # If we upload to the frontends we have to reload the keys
    vagrantdcos_deployment.install_cassandra(ncassandra="6",nseeds="3")
    # TODO: All of this should go into the run procedure
    vagrantdcos_deployment.ycsb_install()
    # Stop here. You have to prepare the cassandra DB
    vagrantdcos_deployment.add_delay(bandwidth="3Mbit",delay="50ms")
    workloads = ["workloada","workloadf"]
    vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "no_fmone",workloads=workloads, recordcount="8000",threadcount="3")
    client, dest_phone, orig_phone = create_twilio_client()
    if client is not None:
        client.messages.create(to=dest_phone,from_=orig_phone,body="Starting the Fmone pipeline. Verify on DC/OS")
    vagrantdcos_deployment.run_fmone_pipeline()
    sleep(380)
    vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "with_fmone",workloads=workloads, recordcount="8000",threadcount="3")
    vagrantdcos_deployment.save_results()
    vagrantdcos_deployment.analyse_results(workloads)


