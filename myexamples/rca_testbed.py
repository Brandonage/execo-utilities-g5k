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
    # new scenarios
    # A loadbalancing scenario
    testbed.lb_wordpress_scenario(nwordpress=10)
    # Don't forget to access the endpoint marathon-lb.marathon.mesos:10001 to configure the wordpress
    testbed.siege_http_clients_scenario(endpoint="marathonlb-loadbalancer-wordpresslb.marathon-user.containerip.dcos.thisdcos.directory:10001",
                                        ninstances=3,
                                        nclients=80,
                                        ntime=2,
                                        time_unit="H",
                                        delay=5)
    testbed.stress_endpoint(endpoint="marathonlb-loadbalancer-wordpresslb.marathon-user.containerip.dcos.thisdcos.directory:10001",
                            ninstances=4,
                            nclients=5,
                            ntime=1,
                            time_unit="M")
    # A hadoop cluster scenario
    testbed.hadoop_cluster_scenario(ndatanodes=3,nnodemanagers=3)
    # The old kafka scenario
    testbed.kafka_producer_consumer_scenario(nbrokers=3,nconsumers=7,nproducers=7)
    testbed.stress_cpu_nodes(nodes=vagrantrca_deployment.private_agents,nstressors=4,timeout=20) # time is in seconds
    testbed.stress_cpu_nodes_random(nnodes=4,nstressors=6,timeout=40)
    testbed.stress_big_heap_nodes(nodes=vagrantrca_deployment.private_agents,nstressors=2,timeout=20)
    testbed.stress_big_heap_nodes_random(nnodes=2,nstressors=2,timeout=20)
    testbed.stress_big_heap_nodes(nodes='10.158.41.41', nstressors=2, timeout=20)
    testbed.stress_disk_nodes_random(nnodes=3,nstressors=3,timeout=20)
    testbed.stress_network_nodes(nodes=vagrantrca_deployment.private_agents,nstressors=2,timeout=10)
    testbed.stress_network_nodes_random(nnodes=2,nstressors=2,timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(nnodes=2,delay='100ms',delay_jitter='50ms',bandwidth='500kbps',loss_percent='5%')
    testbed.limit_upload_bandwidth_nodes(nodes={'10.158.13.94','10.158.13.95','10.158.13.96'},delay='100ms',delay_jitter='50ms',bandwidth='500kbps',loss_percent='5%')

    testbed.restore_upload_bandwidth_nodes(nodes={'10.158.13.94','10.158.13.95','10.158.13.96'})
    vagrantrca_deployment.save_results()

