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
    vagrantdcos_deployment.build_regions(proportions=[33.3333333,33.33333333,33.333333333])

