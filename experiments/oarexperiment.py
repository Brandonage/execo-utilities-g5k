# Class used to create experiments with a classic OAR reservation
from glob import glob
from os import remove, makedirs
from os.path import exists, expanduser
from time import strftime
import pickle


from utils import general_util, submission_util


class OARExperiment:
    jobid = 0  ## The jobid that is linked to this experiment
    nodes = None  ## Set: The nodes that form part of this reservation
    nodesDF = None ## Pandas Dataframe: With information about the different nodes of the reservation

    def __init__(self,frontend,resources,walltime,date,experiment_name,description):
        self.frontend = frontend
        self.resources = resources
        self.walltime = walltime
        self.date = date
        self.experiment_name = experiment_name
        self.description = description
        home = expanduser("~")
        now = strftime("%d_%b_%Y_%H:%M")
        self.results_directory = home + "/execo_experiments/" + self.experiment_name + "__" + now # directory to store results of experiment

    @staticmethod
    def save_experiment(experiment):
        home = expanduser("~")
        output = open(home + "/.experiment","wb")
        pickle.dump(experiment,output)
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
        self.jobid = submission_util.reserve_nodes(self.frontend, self.resources, self.walltime, self.date, self.experiment_name)
        if not self.jobid:
            print "No resources available for this submission"
            quit()

    def deploy_nodes(self):
        deployed, undeployed = submission_util.deploy_nodes(self.frontend, self.jobid)
        if len(undeployed)>0:
            print ("There are undeployed nodes")
        else:
            print ("All nodes deployed")
        self.nodes = deployed
        self.nodesDF = general_util.build_dataframe_of_nodes(self.nodes)
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
        submission_util.clear_reservation(self.frontend, self.jobid)
        [remove(f) for f in glob('hadoop-resources/tmp/*')]
        home = expanduser("~")
        remove(home + "/.experiment")


