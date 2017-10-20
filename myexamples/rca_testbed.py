import sys
from execo import default_connection_params
from os.path import expanduser
# We extend the paths in case we want to upload the experiment to G5K frontend
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/microservices-rca"])
from experiments.rca_vagrantexperiment import RcaVagrantExperiment
from microservices_rca import MicroServicesRCA

if __name__=='main':
    dict = [(7, 4, 10)]  # the format is nnodes,cores,GB
    walltime = "3:25:00"
    experiment_name = "rcavagrant"
    frontend = "nancy"
    description = "Experiments to evaluate an RCA testbed"
    vagrantrca_deployment = RcaVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                 experiment_name=experiment_name, description=description, nmasters=1,
                                                 nprivate_agents=4, npublic_agents=1)
    vagrantrca_deployment.reserve_nodes()
    vagrantrca_deployment.deploy_nodes()
    vagrantrca_deployment.split_dcos_roles()
    vagrantrca_deployment.save_experiment(vagrantrca_deployment)
    vagrantrca_deployment.upload_frontends()
    vagrantrca_deployment = RcaVagrantExperiment.reload_experiment()
    vagrantrca_deployment.reload_keys()
    vagrantrca_deployment.install()
    # we copy the default connection parameters of g5k and change the user and the keyfile
    vagrantrca_deployment.start_monitoring_utils()
    connection_params = default_connection_params.copy()
    connection_params['user'] = 'vagrant'
    connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
    testbed = MicroServicesRCA(vagrantrca_deployment.masters,
                               vagrantrca_deployment.private_agents,
                               vagrantrca_deployment.public_agents,
                               connection_params,
                               'dcos',
                               vagrantrca_deployment.experiment_log
                               )
    testbed.kafka_producer_consumer_scenario(nbrokers=3,nconsumers=8,nproducers=8)
    testbed.stress_cpu_nodes(nodes=vagrantrca_deployment.public_agents,nstressors=4,time=20) # time is in seconds
    testbed.stress_cpu_nodes_random(nnodes=3,nstressors=6,time=40)
    vagrantrca_deployment.save_results()

