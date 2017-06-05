from experiments.dcos_vagrantexperiment import DcosVagrantExperiment
import sys

sys.path.extend(["/home/abrandon/execo-utilities-g5k"])



if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(10,2,4)]
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="rennes"
    description="This is a deployment using vagrant_g5k and DCOS"
    vagrantdcos_deployment = DcosVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                   experiment_name=experiment_name, description=description, nmasters=1,
                                                   nprivate_agents=7, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.install()
    vagrantdcos_deployment.build_regions(proportions=[25, 75], central_region={list(vagrantdcos_deployment.private_agents)[0]})
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.install_cassandra(ncassandra="5",nseeds="3")
    # TODO: All of this should go into the run procedure
    vagrantdcos_deployment.ycsb_install()
    # Stop here. You have to prepare the cassandra DB
    vagrantdcos_deployment.ycsb_run(workload="workloada", recordcount="10000",threadcount="1")
    vagrantdcos_deployment.run()


