from utils.dcos_util import split_dcos_roles
from vagrantexperiment import VagrantExperiment
from utils import general_util
from os.path import expanduser
from itertools import permutations



class DcosVagrantExperiment(VagrantExperiment):
    masters = None
    public_agents = None
    private_agents = None
    bootstrap = None

    def __init__(self, frontend, resources, walltime, experiment_name, description, nmasters, nprivate_agents,
                 npublic_agents, vagrantg5k_path=expanduser("~") + "/vagrant-g5k/"):  # default vagrantg5k path
        VagrantExperiment.__init__(self,frontend,resources,walltime,experiment_name,description,vagrantg5k_path)
        self.nmasters = nmasters
        self.npublic_agents = npublic_agents
        self.nprivate_agents = nprivate_agents
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = self.vagrantg5k_path + 'insecure_private_key'

    def reserve_nodes(self):
        nbootstrap = 1
        # before calling vagrant up lets check if the number of agents and masters equals the nodes specified
        if (sum([r[0] for r in self.resources])) != (nbootstrap + self.nmasters + self.npublic_agents + self.nprivate_agents):
            raise ValueError("The number of VM's is not the same as bootstrap + masters + publicagents + privateagents")
        else:
            VagrantExperiment.reserve_nodes(self)


    def install(self):
        self.bootstrap, self.masters, self.public_agents, self.private_agents = split_dcos_roles(
            self.nodesDF,self.nmasters,self.npublic_agents,self.nprivate_agents
        )
        print "The bootstrap node is: {0}".format(','.join(list(self.bootstrap)))
        print "The masters are: {0}".format(','.join(list(self.masters)))
        print "The public agents are: {0}".format(','.join(list(self.public_agents)))
        print "The private agents are: {0}".format(','.join(list(self.private_agents)))
        print "The DNS server is: {0}".format(general_util.get_dns_server(self.nodesDF.head(1)['ip'][0]))
        print "Don't forget the insecure key"

    def build_regions(self,proportions):
        self.regions = general_util.divide_nodes_into_regions(proportions,list(self.private_agents))
        general_util.limit_bandwith_qdisc(nodes=self.private_agents,netem_idx="10",cap_rate="86Mbit")
        general_util.create_delay_qdisc(nodes=self.private_agents,
                                        netem_idx="10",
                                        delay="100ms",
                                        jitter="0.1ms",
                                        packet_loss="0.1%")
        for (orig_region, dest_region) in permutations(self.regions,2):
            general_util.add_delay_between_regions(orig_region, dest_region,netem_idx="10")

    def run(self):
        pass
