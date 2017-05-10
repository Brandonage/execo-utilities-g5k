from os.path import exists, expanduser
from os import remove, makedirs
from time import strftime
import pickle
from utils import vagrantg5k_util


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
            return experiment
        except IOError:
            print "There is no preserved experiment at $HOME/.experiment"

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
