from experiments.fmone_vagrantexperiment import FmoneVagrantExperiment
import sys
from time import sleep
from aux_utilities.twilio_client import create_twilio_client


sys.path.extend(["/home/abrandon/execo-utilities-g5k"])



if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(22,2,4)]
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="rennes"
    description="This is a deployment using vagrant_g5k and DCOS"
    vagrantdcos_deployment = FmoneVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                    experiment_name=experiment_name, description=description, nmasters=3,
                                                    nprivate_agents=17, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.install()
    # I build the regions and I leave the last private node as the central region
    vagrantdcos_deployment.build_regions(proportions=[33, 33,33], central_region=set(list(vagrantdcos_deployment.private_agents)[-3:]))
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.install_cassandra(ncassandra="5",nseeds="3")
    # TODO: All of this should go into the run procedure
    vagrantdcos_deployment.ycsb_install()
    # Stop here. You have to prepare the cassandra DB
    vagrantdcos_deployment.add_delay(bandwidth="5Mbit",delay="50ms")
    workloads = ["workloada","workloadb","workloade","workloadf"]
    for workload in workloads:
        vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "no_fmone",workload=workload, recordcount="1000",threadcount="1")
    client, dest_phone, orig_phone = create_twilio_client()
    if client is not None:
        client.messages.create(to=dest_phone,from_=orig_phone,body="Starting the Fmone pipeline. Verify on DC/OS")
    vagrantdcos_deployment.run_fmone_pipeline()
    sleep(380)
    for workload in workloads:
        vagrantdcos_deployment.ycsb_run(iterations=5,res_dir = "with_fmone",workload=workload, recordcount="1000",threadcount="1")
    vagrantdcos_deployment.save_results()
    vagrantdcos_deployment.analyse_results()


