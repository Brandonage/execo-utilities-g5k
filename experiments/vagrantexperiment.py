from os.path import exists, expanduser
from os import makedirs
from time import strftime
import pickle
from utils import vagrantg5k_util
from utils.general_util import Put, Get, get_g5k_sites, g5k_configuration


class VagrantExperiment:
    nodes = None
    nodesDF = None

    def __init__(self,frontend,resources,walltime,experiment_name,description,
                 vagrantg5k_path=expanduser("~")+"/vagrant-g5k/"):  # default vagrantg5k path
        self.frontend = frontend
        self.resources = resources # the format is [(nVM's, cpu, mem) .. ] e.g [(4,2,4),(3,2,6)]
        self.walltime = walltime
        self.experiment_name = experiment_name
        self.description = description
        self.vagrantg5k_path = vagrantg5k_path
        home = expanduser("~")
        now = strftime("%d_%b_%Y_%H:%M")
        # directory to store results of experiment
        vagrantg5k_util.vagrantgk5_path  = vagrantg5k_path
        self.results_directory = home + "/execo_experiments/" + self.experiment_name + "__" + now

    @staticmethod
    def save_experiment(experiment):
        home = expanduser("~")
        output = open(home + "/.experiment", "wb")
        pickle.dump(experiment, output)
        output.close()

    @staticmethod
    def reload_experiment():
        home = expanduser("~")
        try:
            input = open(home + "/.experiment", "rb")
            experiment = pickle.load(input)
            input.close()
            # we need to also change the results directory if we want to reload the experiment on a frontend
            home = expanduser("~")
            now = strftime("%d_%b_%Y_%H:%M")
            # directory to store results of experiment
            experiment.results_directory = home + "/execo_experiments/" + experiment.experiment_name + "__" + now
            return experiment
        except IOError:
            print "There is no preserved experiment at $HOME/.experiment"

    def upload_frontends(self):
        """
        Upload the experiment to the frontends in case we want to execute it there
        """
        home = expanduser("~")
        sitesg5k = [s + ".g5k" for s in get_g5k_sites()]
        Put(sitesg5k,
            [home + "/.experiment"],
            connection_params={'user': g5k_configuration.get("g5k_user")}).run()


    def synchronise_with_frontend(self):
        Get(self.frontend + '.g5k',
            remote_files=[".experiment"],
            local_location=expanduser("~") + "/.experiment",
            connection_params={'user': g5k_configuration.get("g5k_user")}
            ).run()

    def reserve_nodes(self):
        """
        Here we will call the vagrant up command and output the results
        """
        print "Calling vagrant up and deploying the VM's in G5K"
        vagrantg5k_util.vagrant_up(self.frontend,self.resources,self.walltime,self.experiment_name)
        pass

    def deploy_nodes(self):
        self.nodesDF, self.nodes = vagrantg5k_util.get_vagrant_nodes()
        self.save_experiment(self)

    def install(self):
        pass

    def describe_cluster(self):
        print self.nodesDF

    def run(self):
        pass

    def save_results(self):
        if not exists(self.results_directory):
            makedirs(self.results_directory)
        self.nodesDF.to_csv("{0}/nodesDF.csv".format(self.results_directory))
        with open("{0}/description.txt".format(self.results_directory), "w") as text_file:
            text_file.write("Description of the experiment: {0}".format(self.description))

    def clean_job(self):
        vagrantg5k_util.vagrant_destroy()

