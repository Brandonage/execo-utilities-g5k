##### CLASS USED TO CREATE EXPERIMENTS
import submission_util
import general_util
from glob import glob
from os import remove

class Experiment:
    jobid = 0  ## The jobid that is linked to this experiment
    nodes = None  ## Set: The nodes that form part of this reservation
    nodesDF = None ## Pandas Dataframe: With information about the different nodes of the reservation

    def __init__(self,frontend,resources,walltime,date,experiment_name):
        self.frontend = frontend
        self.resources = resources
        self.walltime = walltime
        self.date = date
        self.experiment_name = experiment_name

    def reserve_nodes(self):
        self.jobid = submission_util.reserve_nodes(self.frontend,self.resources,self.walltime,self.date,self.experiment_name)
        if not self.jobid:
            print "No resources available for this submission"
            quit()

    def deploy_nodes(self):
        deployed, undeployed = submission_util.deploy_nodes(self.frontend,self.jobid)
        if len(undeployed)>0:
            print ("There are undeployed nodes")
        else:
            print ("All nodes deployed")
        self.nodes = deployed
        self.nodesDF = general_util.build_dataframe_of_nodes(self.nodes)

    def install(self):
        pass

    def describe_cluster(self):
        print self.nodesDF

    def clean_job(self):
        submission_util.clear_reservation(self.frontend,self.jobid)
        [remove(f) for f in glob('hadoop-resources/tmp/*')]


