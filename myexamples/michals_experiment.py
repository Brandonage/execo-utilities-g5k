import sys
from execo import default_connection_params
from os.path import expanduser
from utils import general_util

# We extend the paths in case we want to upload the experiment to G5K frontend
sys.path.extend(["/home/abrandon/execo-utilities-g5k"])
sys.path.extend(["/home/abrandon/microservices-rca"])
from experiments.rca_vagrantexperiment import RcaVagrantExperiment
from microservices_rca import MicroServicesRCA
import time

current_milli_time = lambda: int(round(time.time() * 1000))


class MichalRcaVagrantExperiment(RcaVagrantExperiment):

    def load_cassandra_database(self,cassandra_node):
        general_util.Put(local_files=["aux_utilities/ycsb_init.cql"],
                         hosts=cassandra_node).run()
        general_util.Remote(
            cmd="sudo docker run -v /home/vagrant:/home/vagrant cassandra:3.10 cqlsh -f /home/vagrant/ycsb_init.cql {0}".format(cassandra_node),
            hosts=cassandra_node,
            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
        ).run()

    def load_ycsb_cassandra(self,list_cassandra_nodes, workload):
        general_util.Remote(
            cmd='sudo docker run alvarobrandon/ycsb load cassandra-cql -P ycsb-0.12.0/workloads/{0} -p hosts="{1}" -p recordcount="100000000"'.format(workload,",".join(list_cassandra_nodes)),
            hosts=list_cassandra_nodes[0],
            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
        ).run()

    def save_results(self):
        logs_from_images = ['ches/kafka', 'alvarobrandon/spark-worker', 'alvarobrandon/spark-master',
                            'uhopper/hadoop-datanode:2.8.1', 'uhopper/hadoop-namenode:2.8.1', 'zookeeper',
                            'mesosphere/marathon-lb:v1.11.1','alvarobrandon/spark-bench','']
        # Extract here from the marathon API all the Mesos TaskIDs for the different applications
        for agent in self.private_agents:
            for image in logs_from_images:
                p = general_util.SshProcess('sudo docker ps -f "ancestor={0}" -q -a'.format(image),
                                            host=agent).run()
                image_dir = image.replace('/', '_')
                for containerid in p.stdout.split('\r\n')[:-1]:
                    if image == 'alvarobrandon/spark-worker':
                        print(containerid,image_dir)
                    p = general_util.SshProcess('mkdir /home/vagrant/{0}_{1}_logs'.format(image_dir, containerid),
                                                host=agent).run()
                    p = general_util.SshProcess(
                        'sudo docker logs {1} >> /home/vagrant/{0}_{1}_logs/stdout_{0}_{1}.out 2>&1'.format(image_dir, containerid),
                        host=agent).run()
                    if image == 'ches/kafka': # if image_dir is kafka then copy some extra logs
                        p = general_util.SshProcess(
                            'sudo docker cp {1}:/kafka/logs /home/vagrant/{0}_{1}_logs/'.format(image_dir, containerid),
                            host=agent).run()
                    if image == 'alvarobrandon/spark-worker': # if image_dir is spark copy the extra logs
                        p = general_util.SshProcess(
                            'sudo docker cp {1}:/spark/work/ /home/vagrant/{0}_{1}_logs/'.format(image_dir, containerid),
                            host=agent).run()
        RcaVagrantExperiment.save_results(self)
        # clean the jars first since we don't want them
        general_util.Remote(hosts=self.private_agents,
                            cmd="sudo rm -f /home/vagrant/*/work/*/*/spark-bench-2.1.1_0.3.0-RELEASE.jar").run()
        general_util.Remote(hosts=self.private_agents,
                            cmd="sudo rm /home/vagrant/*.scrap.gz").run()
        general_util.Get(hosts=self.private_agents,
                         remote_files=["/home/vagrant/"],
                         local_location=self.results_directory).run()



if __name__ == 'main':
    dict = [(8, 4, 10)]  # the format is nnodes,cores,GB
    walltime = "3:25:00"
    experiment_name = "rcavagrant"
    frontend = "nancy"
    description = "Experiments to evaluate an RCA testbed"
    vagrantrca_deployment = MichalRcaVagrantExperiment(frontend=frontend, resources=dict, walltime=walltime,
                                                       experiment_name=experiment_name, description=description,
                                                       nmasters=1,
                                                       nprivate_agents=5, npublic_agents=1)
    vagrantrca_deployment.reserve_nodes()
    vagrantrca_deployment.deploy_nodes()
    vagrantrca_deployment.split_dcos_roles()
    vagrantrca_deployment.save_experiment(vagrantrca_deployment)
    vagrantrca_deployment.upload_frontends()
    vagrantrca_deployment = RcaVagrantExperiment.reload_experiment()
    vagrantrca_deployment.reload_keys()  # we copy the default connection parameters of g5k and change the user and the keyfile
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
    testbed.kafka_producer_consumer_scenario(nbrokers=4, nconsumers=12, nproducers=12)
    # KILL SOME KAFKA BROKERS HERE
    testbed.kill_container_id('10.136.107.16', '56ded3cd86b1')
    testbed.kill_container_id('10.136.107.16', '2b3eb8c99b60')
    testbed.kill_container_id('10.136.107.14', '18be91deee10')
    #
    #
    testbed.spark_standalone_scenario(ndatanodes=4,
                                      nslaves=4)
    # KILL 2 SPARK WORKERS
    testbed.kill_container_id('10.136.107.16', '045e1c812237')
    # KILL 2 HDFS DATANODES
    testbed.kill_container_id('10.136.107.14', 'e4fdb5918371')
    testbed.cassandra_cluster_scenario(nnodes=3)
    list_of_cassandra_nodes = ['1234','1231']
    vagrantrca_deployment.load_cassandra_database('whatever cassandra node') # give format to the keyspace in cassadnra database
    vagrantrca_deployment.load_ycsb_cassandra(list_of_cassandra_nodes,'workloada') # use ycsb to load the data into cassandra
    testbed.ycsb_cassandra_client_scenario(3,list_of_cassandra_nodes,'workloada')

    vagrantrca_deployment.save_results()
