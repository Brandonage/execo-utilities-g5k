import sys
# We extend the paths in case we want to upload the experiment to G5K frontend
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks"])
from experiments.fmone_vagrantexperiment import FmoneVagrantExperiment
from time import sleep
from aux_utilities.twilio_client import create_twilio_client



if __name__ == '__main__':
    #dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["griffon-17.nancy.grid5000.fr","griffon-16.nancy.grid5000.fr"],2)]}
    dict = [(10,4,10)] # the format is nnodes,cores,GB
    walltime = "3:25:00"
    experiment_name="dcosvagrant"
    frontend="nancy"
    description="This experiment evaluates the elasticity of Fmone"
    vagrantdcos_deployment = FmoneVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                    experiment_name=experiment_name, description=description, nmasters=1,
                                                    nprivate_agents=7, npublic_agents=1)
    vagrantdcos_deployment.reserve_nodes()
    vagrantdcos_deployment.deploy_nodes()
    vagrantdcos_deployment.split_dcos_roles()
    vagrantdcos_deployment.save_experiment(vagrantdcos_deployment)
    vagrantdcos_deployment.upload_frontends()
    vagrantdcos_deployment = FmoneVagrantExperiment.reload_experiment()
    vagrantdcos_deployment.reload_keys() # If we upload to the frontends we have to reload the keys
    vagrantdcos_deployment.install()
    # I build the regions
    vagrantdcos_deployment.build_regions(proportions=[100], central_region=set(list(vagrantdcos_deployment.private_agents)))
    i = 0
    for r in vagrantdcos_deployment.regions: # all but the central region. Note that when the regions are built the central region is appended last
        vagrantdcos_deployment.run_fmone_pipeline(pipeline_type="regional_mongo",
                                                  slaves=str(r.__len__()),
                                                  region=str(i))
        i=i+1