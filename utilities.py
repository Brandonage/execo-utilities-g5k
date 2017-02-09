##
##  THIS FILE WILL INCLUDE UTILITIES THAT WILL BE USED BY EXTERNAL AND INTERNAL SCRIPTS
##
##
##
from execo import *
from execo_g5k import *


##(nodes:A list of nodes that are returned by the get_oar_job_nodes(jobid,site) function)
def build_dataframe_of_resources(nodes): ## It will return a Pandas Dataframe with the network, disk, CPU and other resources for the different nodes.
    for node in nodes:                   ## This will allow us to order the Dataframe by CPU speed, disk and so on
        get_host_attributes(node)

