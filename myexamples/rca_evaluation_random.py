import sys
from execo import default_connection_params
from os.path import expanduser

# We extend the paths in case we want to upload the experiment to G5K frontend
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/microservices-rca"])
from experiments.rca_vagrantexperiment import RcaVagrantExperiment
from microservices_rca import MicroServicesRCA
import time

current_milli_time = lambda: int(round(time.time() * 1000))

if __name__ == 'main':
    dict = [(8, 4, 10)]  # the format is nnodes,cores,GB
    walltime = "3:25:00"
    experiment_name = "rcavagrant"
    frontend = "nancy"
    description = "Experiments to evaluate an RCA testbed"
    vagrantrca_deployment = RcaVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                 experiment_name=experiment_name, description=description, nmasters=1,
                                                 nprivate_agents=5, npublic_agents=1)
    vagrantrca_deployment.reserve_nodes()
    vagrantrca_deployment.deploy_nodes()
    vagrantrca_deployment.split_dcos_roles()
    vagrantrca_deployment.save_experiment(vagrantrca_deployment)
    vagrantrca_deployment.upload_frontends()
    vagrantrca_deployment = RcaVagrantExperiment.reload_experiment()
    vagrantrca_deployment.reload_keys() # we copy the default connection parameters of g5k and change the user and the keyfile
    vagrantrca_deployment.install()
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
    # This is a template on how to add a row to the experiment log.
    testbed.write_to_experiment_log(current_milli_time(), "anomaly", "wrong_lb_conf", "marathon-lb.marathon.mesos",
                                    1547888859, 1547888946, "Unbalanced configuration to tasks X and Y")
    marathon_node = {'10.136.41.154'}
    testbed.kafka_producer_consumer_scenario(nbrokers=4, nconsumers=12, nproducers=12)
    # ROUND A - CPU STRESS
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)  # time is in seconds
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)
    # ROUND B - LIMIT BANDWITH
    testbed.limit_upload_bandwidth_nodes_random(2, leave_out=marathon_node, delay='100ms', delay_jitter='50ms',
                                                bandwidth='75kbps', loss_percent='5%', timeout=15)
    testbed.limit_upload_bandwidth_nodes_random(2, leave_out=marathon_node, delay='100ms', delay_jitter='50ms',
                                                bandwidth='75kbps', loss_percent='5%', timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(2, leave_out=marathon_node, delay='100ms', delay_jitter='50ms',
                                                bandwidth='75kbps', loss_percent='5%', timeout=20)
    # ROUND C - STRESS DISK
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)  # time is in seconds
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=15, leave_out=marathon_node)
    # ROUND D - STRESS NETWORK
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    # ROUND E - BIG HEAP MEMORY
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15, leave_out=marathon_node)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15, leave_out=marathon_node)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15, leave_out=marathon_node)
    # ROUND F - BIG HEAP MEMORY
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)

    # LoadBalancer Scenario
    # There is a way of referencing the host where the loadbalancer is
    # marathonlb-loadbalancer-wordpresslb.marathon-user.agentip.dcos.thisdcos.directory
    testbed.lb_wordpress_scenario(nwordpress=16)
    # STOP HERE! : Configure the wordpress and open the haproxy?stats page
    testbed.ab_clients_scenario(endpoint="10.136.41.158:6723",
                                ninstances=6,
                                nclients=12,
                                nrequests=1000000,
                                )
    # FOR THE AB CLIENTS: 12N CLIENTS FOR NORMAL CONDITIONS AND 5 INSTANCES, 14N CLIENTS FOR WRONG LB AND 5 INSTANCES
    # testbed.siege_http_clients_scenario(endpoint="marathonlb-loadbalancer-wordpresslb.marathon-user.containerip.dcos.thisdcos.directory:10001",
    #                                     ninstances=2,
    #                                     nclients=10,
    #                                     ntime=2,
    #                                     time_unit="H",
    #                                     delay=15)
    # ROUND A - CPU STRESS
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)  # time is in seconds
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)
    # ROUND B - LIMIT BANDWITH
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    # ROUND C - STRESS DISK
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)  # time is in seconds
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)
    # ROUND D - STRESS NETWORK
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    # ROUND E - BIG HEAP MEMORY
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    # ROUND F - BIG HEAP MEMORY
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    # ROUND UNBALANCED LB
    testbed.write_to_experiment_log(current_milli_time(), "anomaly", "wrong_lb_conf", "marathon-lb.marathon.mesos",
                                    int(time.time()), int(time.time()) + 15,
                                    "Unbalanced configuration to tasks X and Y")
    testbed.write_to_experiment_log(current_milli_time(), "anomaly", "wrong_lb_conf", "marathon-lb.marathon.mesos",
                                    int(time.time()), int(time.time()) + 60,
                                    "Unbalanced configuration to tasks X and Y")
    testbed.write_to_experiment_log(current_milli_time(), "anomaly", "wrong_lb_conf", "marathon-lb.marathon.mesos",
                                    int(time.time()), int(time.time()) + 60,
                                    "Unbalanced configuration to tasks X and Y")
    # ROUND G - STRESS ENDPOINTS
    # This anomalies have to be done by hand
    testbed.stress_endpoint_ab(endpoint="10.136.61.140:14966",
                               ninstances=9,
                               nclients=30,
                               nrequests=10000000,
                               timein=60)
    testbed.stress_endpoint_ab(endpoint="10.144.87.128:10324",
                               ninstances=8,
                               nclients=30,
                               nrequests=10000000,
                               timein=20)
    testbed.stress_endpoint_ab(endpoint="10.144.87.128:10324",
                               ninstances=8,
                               nclients=30,
                               nrequests=10000000,
                               timein=20)
    # testbed.stress_endpoint(endpoint="marathonlb-loadbalancer-wordpresslb.marathon-user.containerip.dcos.thisdcos.directory:10001",
    #                         ninstances=4,
    #                         nclients=5,
    #                         ntime=30,
    #                         time_unit="S")

    # Spark-HDFS Scenario
    testbed.spark_standalone_scenario(ndatanodes=4,
                                      nslaves=4)
    # Remember to launch the spark-bench container to generate the workload.
    # ROUND A - CPU STRESS
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)  # time is in seconds
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_cpu_nodes_random(2, nstressors=6, timeout=20)
    # ROUND B - LIMIT BANDWITH
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    testbed.limit_upload_bandwidth_nodes_random(2, delay='100ms', delay_jitter='50ms', bandwidth='75kbps',
                                                loss_percent='5%', timeout=20)
    # ROUND C - STRESS DISK
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)  # time is in seconds
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_disk_nodes_random(2, nstressors=6, timeout=20)
    # ROUND D - STRESS NETWORK
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    testbed.stress_network_nodes_random(2, nstressors=6, timeout=20)
    # ROUND E - BIG HEAP MEMORY
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    testbed.stress_big_heap_nodes_random(2, nstressors=1, timeout=15)
    # ROUND F - BIG HEAP MEMORY
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    testbed.stress_zlib_nodes_random(2, nstressors=1, timeout=20)
    # testbed.hadoop_cluster_scenario(3,3)
    vagrantrca_deployment.save_results()
