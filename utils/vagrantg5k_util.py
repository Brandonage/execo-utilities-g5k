from os.path import expanduser
from subprocess import check_output
from pandas import DataFrame

home = expanduser("~")
# we need an attribute that points to wherever the vagrant-g5k VagrantFile is
vagrantgk5_path = home + "/vagrant-g5k/"  # This will be changed by the vagrantexperiment class too at creation time


def get_vagrant_nodes():
    output = check_output(
        "cd " + vagrantgk5_path + " && vagrant ssh-config | grep -e \"^Host \" -e HostName | awk '{print $2}'", shell=True)
    splitted = output.split("\n")[:-1] # e.g ['test-1','10.158.0.3','test-2','10.158.0.1','test-3','10.158.3.254']
    # nodesmap = dict(zip(splitted[::2],splitted[1::2]))
    d = {"ip": splitted[1::2],
         "name": splitted[::2]}
    nodesDF = DataFrame(d)
    nodes = set(splitted[1::2])
    return nodesDF, nodes


def vagrant_up(frontend,resources,walltime,experiment_name):
    pass

def vagrant_destroy():
    pass
