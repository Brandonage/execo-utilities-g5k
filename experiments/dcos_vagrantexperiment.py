from utils.dcos_util import split_dcos_roles, prepare_config_yaml
from utils import fmone_util
from experiments.vagrantexperiment import VagrantExperiment
from utils import general_util
from os.path import expanduser
from itertools import permutations
import sys



class DcosVagrantExperiment(VagrantExperiment):
    masters = None
    public_agents = None
    private_agents = None
    bootstrap = None
    dns_resolver = None

    def __init__(self, frontend, resources, walltime, experiment_name, description, nmasters, nprivate_agents,
                 npublic_agents, vagrantg5k_path=expanduser("~") + "/vagrant-g5k/"):  # default vagrantg5k path
        VagrantExperiment.__init__(self,frontend,resources,walltime,experiment_name,description,vagrantg5k_path)
        self.nmasters = nmasters
        self.npublic_agents = npublic_agents
        self.nprivate_agents = nprivate_agents
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

    def reserve_nodes(self):
        nbootstrap = 1
        # before calling vagrant up lets check if the number of agents and masters equals the nodes specified
        if (sum([r[0] for r in self.resources])) != (nbootstrap + self.nmasters + self.npublic_agents + self.nprivate_agents):
            raise ValueError("The number of VM's is not the same as bootstrap + masters + publicagents + privateagents")
        else:
            VagrantExperiment.reserve_nodes(self)


    def install(self):
        # TODO: THIS SHOULD ALL GO INTO THE DCOS_UTIL FILE AS A FUNCTION "INSTALL DCOS"
        # E.G INSTALL_DCOS(NODESDF,NMASTERS,NPAGENTS,NPRIVAGENTS)
        config_yaml_output = "dcos-resources/config.yaml"
        ip_detect_file = "dcos-resources/ip-detect"
        # First, split the roles
        self.bootstrap, self.masters, self.public_agents, self.private_agents = split_dcos_roles(
            self.nodesDF,self.nmasters,self.npublic_agents,self.nprivate_agents
        )
        # We need the dns resolver that the nodes use
        self.dns_resolver = general_util.get_dns_server(self.nodesDF.head(1)['ip'][0])
        # With all this information we build the config.yaml file necessary for the installation
        prepare_config_yaml(self.masters,self.private_agents,self.public_agents,self.dns_resolver,config_yaml_output)
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
        general_util.Remote("curl -O https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh",
                            hosts=self.bootstrap,
                            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}).run()
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
            if i==(len(self.regions)-1):
                region_name = "regioncentral"
            else:
                region_name = "region" + str(i)
            with open("mesos-slave-common","w") as f:
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
            print "The region {0} has the nodes: {1}".format(region_name,self.regions[i])

    def run(self,nslaves):
        general_util.limit_bandwith_qdisc(nodes=self.private_agents,netem_idx="10",cap_rate="86Mbit")
        general_util.create_delay_qdisc(nodes=self.private_agents,
                                        netem_idx="10",
                                        delay="100ms",
                                        jitter="0.1ms",
                                        packet_loss="0.1%")
        for (orig_region, dest_region) in permutations(self.regions,2):
            general_util.add_delay_between_regions(orig_region, dest_region,netem_idx="10")
        fmone_util.execute_pipeline("central_mongo",{"@nslaves@" : "95", "@region@" : "central"},
                                    self.masters,general_util.default_connection_params)

