from utils import dcos_util
from utils import fmone_util
from experiments.vagrantexperiment import VagrantExperiment
from utils import general_util
from os.path import exists, expanduser
from os import makedirs
from itertools import permutations
import sys
import warnings
from time import strftime
import json
from distutils.dir_util import copy_tree
from shutil import rmtree


sys.path.extend(["/home/abrandon/execo-g5k-benchmarks/ycsb"])

from ycsb.cassandraycsb import CassandraYCSB


class FmoneVagrantExperiment(VagrantExperiment):
    masters = None
    public_agents = None
    private_agents = None
    bootstrap = None
    dns_resolver = None

    def __init__(self, frontend, resources, walltime, experiment_name, description, nmasters, nprivate_agents,
                 npublic_agents, vagrantg5k_path=expanduser("~") + "/vagrant-g5k/"):  # default vagrantg5k path
        VagrantExperiment.__init__(self, frontend, resources, walltime, experiment_name, description, vagrantg5k_path)
        self.nmasters = nmasters
        self.npublic_agents = npublic_agents
        self.nprivate_agents = nprivate_agents
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        dcos_util.default_connection_params['user'] = 'vagrant'
        dcos_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

    def reload_keys(self):
        """
        Use it to reload the execo connection parameters with the ssh vagrant keys and the vagrant user
        """
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        dcos_util.default_connection_params['user'] = 'vagrant'
        dcos_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

    def reserve_nodes(self):
        nbootstrap = 1
        # before calling vagrant up lets check if the number of agents and masters equals the nodes specified
        if (sum([r[0] for r in self.resources])) != (
                            nbootstrap + self.nmasters + self.npublic_agents + self.nprivate_agents):
            raise ValueError("The number of VM's is not the same as bootstrap + masters + publicagents + privateagents")
        else:
            VagrantExperiment.reserve_nodes(self)

    def split_dcos_roles(self):
        # First, split the roles
        self.bootstrap, self.masters, self.public_agents, self.private_agents = dcos_util.split_dcos_roles(
            self.nodesDF, self.nmasters, self.npublic_agents, self.nprivate_agents
        )

    def install(self):
        # TODO: THIS SHOULD ALL GO INTO THE DCOS_UTIL FILE AS A FUNCTION "INSTALL DCOS"
        # E.G INSTALL_DCOS(NODESDF,NMASTERS,NPAGENTS,NPRIVAGENTS)
        config_yaml_output = "dcos-resources/config.yaml"
        ip_detect_file = "dcos-resources/ip-detect"
        # We need the dns resolver that the nodes use
        self.dns_resolver = general_util.get_dns_server(self.nodesDF.head(1)['ip'][0])
        # With all this information we build the config.yaml file necessary for the installation
        dcos_util.prepare_config_yaml(self.masters, self.private_agents, self.public_agents, self.dns_resolver,
                                      config_yaml_output)
        # Here we start preparing all the files needed to launch the installation script
        # That means: create genconf directory, config.yaml, ip-detect, upload the ssh key
        general_util.Remote("mkdir -p /home/vagrant/genconf", hosts=self.bootstrap).run()
        general_util.Put(hosts=self.bootstrap,
                         local_files=[config_yaml_output],
                         remote_location="/home/vagrant/genconf/config.yaml").run()
        general_util.Put(hosts=self.bootstrap,
                         local_files=[ip_detect_file],
                         remote_location="/home/vagrant/genconf/ip-detect").run()
        general_util.Put(hosts=self.bootstrap,
                         local_files=[expanduser("~") + "/.vagrant.d/insecure_private_key"],
                         remote_location="/home/vagrant/genconf/ssh_key").run()
        # We now start the installation process
        # We put the generate_config.sh directly from our local directory to the bootstrap machine
        general_util.Put(hosts=self.bootstrap,
                         local_files=[expanduser("~") + "/vagrant-g5k/resources/dcos_generate_config.sh"],
                         remote_location="/home/vagrant/dcos_generate_config.sh"
                         ).run()
        general_util.Remote("sudo bash dcos_generate_config.sh --genconf",
                            hosts=self.bootstrap,
                            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}).run()
        general_util.Remote("sudo bash dcos_generate_config.sh --preflight",
                            hosts=self.bootstrap,
                            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}).run()
        general_util.Remote("sudo bash dcos_generate_config.sh --deploy",
                            hosts=self.bootstrap,
                            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}).run()
        general_util.Remote("sudo bash dcos_generate_config.sh --postflight",
                            hosts=self.bootstrap,
                            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}).run()
        dcos_util.install_dcos_cli(self.masters.union(self.private_agents))
        print "The bootstrap node is: {0}".format(','.join(list(self.bootstrap)))
        print "The masters are: {0}".format(','.join(list(self.masters)))
        print "The public agents are: {0}".format(','.join(list(self.public_agents)))
        print "The private agents are: {0}".format(','.join(list(self.private_agents)))
        print "The DNS server is: {0}".format(general_util.get_dns_server(self.nodesDF.head(1)['ip'][0]))

    def build_regions(self, proportions, central_region):
        # we divide the nodes into regions without considering what it will be the master region
        """
        The vagrant experiment has the ability to split its private agents into regions
        :param proportions: the proportions in which we want to split the private_nodes
        :param central_region: the machine that is going to act as central region. It is going to normally hold
        the Marathon user service and all the centralised cloud services
        """
        self.regions = general_util.divide_nodes_into_regions(proportions,
                                                              list(self.private_agents.difference(central_region))
                                                              )
        # we now include the central region
        self.regions.append(central_region)
        for i in xrange(len(self.regions)):
            if i == (len(self.regions) - 1):
                region_name = "regioncentral"
            else:
                region_name = "region" + str(i)
            with open("mesos-slave-common", "w") as f:
                f.write("MESOS_ATTRIBUTES=region:{0}".format(region_name))
            # it's not possible to ssh as root into a guest VM. We will copy the file to home and then sudo cp
            general_util.Put(hosts=self.regions[i], local_files=["mesos-slave-common"],
                             remote_location="/home/vagrant").run()
            general_util.Remote("sudo cp /home/vagrant/mesos-slave-common /var/lib/dcos/mesos-slave-common",
                                hosts=self.regions[i]).run()
            # we reinitialise the slaves for the attributes to be taken into account
            general_util.Remote("sudo systemctl stop dcos-mesos-slave",
                                hosts=self.regions[i]).run()
            general_util.Remote("sudo rm -f /var/lib/mesos/slave/meta/slaves/latest",
                                hosts=self.regions[i]).run()
            general_util.Remote("sudo systemctl start dcos-mesos-slave",
                                hosts=self.regions[i]).run()
            print "The region {0} has the nodes: {1}".format(region_name, self.regions[i])

    def install_cassandra(self, ncassandra, nseeds):
        master = list(self.masters)[0]
        # print "Execute this command in the machine {0}: dcos package install --yes --options=cassandra-config.json cassandra" \
        #     .format(master_name)
        # print "And this: dcos package install cassandra --cli"
        # raw_input("After executing press enter: ")
        self.cassandra_nodes = dcos_util.install_cassandra(masternode=master, ncassandra=ncassandra,
                                                           nseeds=nseeds)
        general_util.Put(local_files=["aux_utilities/ycsb_init.cql"],
                         hosts=self.cassandra_nodes).run()
        general_util.Remote(
            cmd="sudo docker run -v /home/vagrant:/home/vagrant cassandra:3.10 cqlsh -f /home/vagrant/ycsb_init.cql {{{host}}}",
            hosts=list(self.cassandra_nodes)[0],
            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
        ).run()

    def ycsb_install(self):
        # We will install yscb only in one node per region
        nodes_to_install = set([list(region)[0] for region in self.regions])
        # we move the ycsb benchmark that we rsynced to home in order for the CassandraYCSB class to take care of all
        #  the installation process
        general_util.Put(local_files=[expanduser("~") + "/vagrant-g5k/resources/ycsb-0.12.0.tar.gz"],
                         hosts=nodes_to_install).run()
        general_util.install_JDK_8(nodes_to_install, os="centos")
        self.cassandra_ycsb = CassandraYCSB(install_nodes=nodes_to_install,
                                            execo_conn_params=general_util.default_connection_params,  # needed by execo
                                            cassandra_nodes=self.cassandra_nodes)  # the nodes where cassandra is installed

    def ycsb_run(self, iterations, res_dir, workloads, recordcount, threadcount, fieldlength, target):
        # we build a list of single elements sets with the nodes that will run the yscb workload
        """
        Run a series of workloads a number of iterations and save the results in a directory
        :param iterations: the number of times to execute each workload
        :param res_dir: the directory in which to store the results
        :param workloads: the different workloads that we want to execute
        :param recordcount: the number of records that will be inserted
        :param threadcount: the number of threads for each client
        """
        yscb_clients = self.cassandra_ycsb.install_nodes
        # create a directory for the results
        general_util.Remote(cmd="mkdir " + res_dir, hosts=yscb_clients).run()
        for workload in workloads:
            self.cassandra_ycsb.load_workload(from_node=yscb_clients,
                                              workload=workload,
                                              recordcount=recordcount,
                                              threadcount=threadcount,
                                              fieldlength=fieldlength)
            for i in range(iterations):
                self.cassandra_ycsb.run_workload(iteration=i,
                                                 res_dir=res_dir,
                                                 from_node=yscb_clients,
                                                 workload=workload,
                                                 recordcount=recordcount,
                                                 threadcount=threadcount,
                                                 fieldlength=fieldlength,
                                                 target=target)

    def add_delay(self, delay, bandwidth):
        general_util.limit_bandwith_qdisc(nodes=self.private_agents, netem_idx="10", cap_rate=bandwidth)
        general_util.create_delay_qdisc(nodes=self.private_agents,
                                        netem_idx="10",
                                        delay=delay,
                                        jitter="0.1ms",
                                        packet_loss="0.5%")
        for (orig_region, dest_region) in permutations(self.regions, 2):
            general_util.add_delay_between_regions(orig_region, dest_region, netem_idx="10")

    def run_fmone_pipeline(self):
        fmone_util.execute_pipeline("central_ycsb",
                                    {"@nslaves@": str(self.private_agents.__len__()), "@region@": "central"},
                                    self.masters, general_util.default_connection_params)

    def save_results(self):
        VagrantExperiment.save_results(self)
        yscb_clients = self.cassandra_ycsb.install_nodes
        general_util.Get(hosts=yscb_clients,
                         remote_files=["with_fmone", "no_fmone"],
                         local_location=self.results_directory).run()
        copy_tree(".netcheck", self.results_directory)
        rmtree(".netcheck")


    def analyse_results(self, workloads):
        directories = ["/with_fmone", "/no_fmone"]
        results = {}
        for d in directories:
            for w in workloads:
                list_of_metrics, metrics_mean = self.cassandra_ycsb.analyse_output(directory=self.results_directory + d,
                                                                                   workload=w,
                                                                                   metric="Throughput")
                results[w + d] = (list_of_metrics, metrics_mean)
                print "For workload {0} and {1} the mean throughput is: {2}".format(w, d, metrics_mean)

    def remove_node(self, node):
        """
        Use this method to remove a node from the experiment
        """
        i = 0
        for set_nodes in self.regions:  # for each region
            if node in set_nodes:  # if the node is in the region
                self.regions[i].remove(node)  # we remove it
                region = self.regions[i]  # and we save the region to find a replacement for the substituted one
            i = i + 1
        try:
            self.nodesDF = self.nodesDF[self.nodesDF['ip'] != node]
            self.nodes.remove(node)
            self.private_agents.remove(node)
            self.cassandra_nodes.remove(node)
            self.cassandra_ycsb.install_nodes.remove(node)
            substitute = list(region)[0]
            self.cassandra_ycsb.install_nodes.add(substitute)
            print "Substituted {0} by {1}. Please install YCSB in this node"
        except AttributeError:
            warnings.warn("There were some attributes missing. Removing node in all possible parts of experiment",
                          UserWarning)

    def checkpoint_network(self):
        """
        This method will export to a temporary directory the state of the network interface for the node that is running
        the u'/fmoncentralpipecentral/mongoccentral/mongocentralcentral' task. We do this to check how much traffic does
        the central node receives with a centralised approach
        """
        netcheck_directory = ".netcheck"
        curl_node = list(self.masters)[0]
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout)
        mongo_tasks = filter(lambda task: task['appId'] == u'/fmoncentralpipecentral/mongoccentral/mongocentralcentral',
               d.get('tasks'))
        mongo_host = mongo_tasks[0]['host']
        p = general_util.SshProcess('/sbin/ifconfig',
                                    host=mongo_host,
                                    shell=True,
                                    pty=True).run()
        now = strftime("%d_%b_%Y_%H:%M")
        if not exists(netcheck_directory):
            makedirs(netcheck_directory)
        with open('.netcheck/net_checkpoint' + now,'w') as f:
            f.write(p.stdout)


