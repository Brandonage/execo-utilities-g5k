from utils import dcos_util, general_util, monitoring_util
from experiments.vagrantexperiment import VagrantExperiment
from os.path import expanduser

"""
This class is going to represent a RCA experiment with DCOS, where we experiment
with different microservices workflows and we inject failures in its components.
The aim is to monitor and observe the behaviour of these containers in the G5K
testbed
"""
class RcaVagrantExperiment(VagrantExperiment):
    # Necessary attribute for DCOS.
    # We will assign the values during creation and installation of DCOS and not at the beginning
    masters = None
    public_agents = None
    private_agents = None
    bootstrap = None
    dns_resolver = None

    """
    Initiate all the parameters and configure the connection parameters to the nodes for both the general utils and dcos
    """
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
        # There are going to be monitoring tools involved on this experiments so we install them
        monitoring_util.default_connection_params['user'] = 'vagrant'
        monitoring_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

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
        # We need the dns resolver that the nodes use
        self.dns_resolver = general_util.get_dns_server(self.nodesDF.head(1)['ip'][0])
        # We call the method from dcos_util that installs everything
        dcos_util.install_dcos(self.bootstrap,self.masters,self.public_agents,self.private_agents,self.dns_resolver)
        monitoring_util.install_dstat(self.nodes,'centos')

