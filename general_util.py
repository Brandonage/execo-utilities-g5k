##
##  THIS FILE WILL INCLUDE UTILITIES THAT WILL BE USED BY EXTERNAL AND INTERNAL SCRIPTS
##
##
##
from execo import *
from execo_g5k import *
from jsonpath_rw import jsonpath, parse
from numpy import mean, nan
from pandas import DataFrame
from custom_output_handler import PyConsoleOutputHandler
bytes_in_gigabyte = 1073741824 ## The number of bytes in one gigabyte
bytes_in_megabyte = 1048576
wget_destination = "/opt" ## This is where we are going to untar all the wget files

## (node_dict : Dict with the JSON of querying the Grid5k API, resource: String, the name of the resource)
## RETURNS: A representation in int,boolean or unique values of that resource for the node
## (We use the jsonpath library to add the path inside the JSON of each resource)
def get_resource(node_dict,resource):
    parse_dict = { ## We start by creating parsers that will extract the information from the JSON structure
        "power_available":"sensors.power.available",
        "node_flops":"performance.node_flops",
        "CPU description":"processor.other_description",
        "PDU":"sensors.power.via.pdu[*].uid",
        "GPU":"gpu.gpu",
        "SSD":"storage_devices[*].storage",
        "HDD":"storage_devices[*].storage",
        "storage_size":"storage_devices[*].size",
        "RAM":"main_memory.ram_size",
        "cores":"architecture.nb_cores",
    }
    jsonpath_expr = parse(parse_dict.get(resource))
    list_of_results = [match for match in jsonpath_expr.find(node_dict)]## Get a list of data from the JSON that matches that pattern
    ##Different resources will have different semantics for their values. We get them through the following if statements
    if (resource in ["power_available","node_flops","CPU description","GPU","cores"]):##if the resource has a unique value
        return list_of_results[0].value ##return the single value
    if (resource=="PDU"):
        values = [res.value for res in list_of_results ] ## get the values of the list of one element
        return ' and '.join(values) ## We want a string with the different PDU's
    if (resource in ["SSD","HDD"]):
        values = [res.value for res in list_of_results if res.value==resource ] ## We get a list with the different types of storage that node has (e.g. SSD, HDD)
        capacity = [res.context.value.get("size") for res in list_of_results if res.value==resource] ## We get a list with the size of storage for each disk of that type
        if values: ## If we have values
            return str(values.count(resource)) + " * " + str(int(mean(capacity)/bytes_in_gigabyte)) + " GB"## We want the number of SSD's disk on the node and the mean capacity of this number
        else: ## If not return empty string
            return nan
    if (resource in ["storage_size","RAM"]):
        values = [res.value for res in list_of_results ]
        return sum(values)/bytes_in_gigabyte ## We want the sum of all the storage in that node





##(nodes:A list of nodes that are returned by the get_oar_job_nodes(jobid,site) function)
## It will return a Pandas Dataframe with the network, disk, CPU and other resources for the different nodes.
## This will allow us to order the Dataframe by CPU speed, disk and so on
def build_dataframe_of_nodes(nodes):
    d = {}  ## we will build the dataframe with this dictionary
    resources = ["power_available","node_flops","CPU description","PDU","GPU","SSD","HDD","storage_size","RAM","cores"]## This is a list of the resources we want to query
    list_of_nodes_dict = [get_host_attributes(node) for node in nodes] ## get the information of the list of nodes
    for resource in resources: ## For each resource
        values = [get_resource(node_dict,resource) for node_dict in list_of_nodes_dict] ## Get a list of the values for that resource
        d.update({resource:values}) #update the list
    d.update({"node_name":list(nodes)}) ## We need three additional fields that are outside the list of dictionaries. First the name of nodes
    d.update({"cluster":[get_host_cluster(node) for node in nodes]}) ## The name of the cluster
    d.update({"site":[get_host_site(node) for node in nodes]})
    return DataFrame(d)

### infile: String with the file in, outfile: String with the file out, substitutions: dictionary of substitutions
def replace_infile(pathin,pathout,replacements):
    with open(pathin) as infile, open(pathout, 'w') as outfile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            outfile.write(line)


##(nodesDF: A pandas dataframe with all the information about your nodes)
## RETURNS: an string with the name of the master node
def node_with_smaller_memory(nodesDF):
    return set([nodesDF.sort_values(by="RAM").iloc[0]["node_name"]])

##(nodesDF: A pandas dataframe with all the information about your nodes)
## RETURNS: a set with the names of the N Nodes with bigger storage capacity.
def nodes_with_largest_storage(nodesDF,nNodes):
    return set(nodesDF.sort_values(by="storage_size",ascending=False).head(nNodes)["node_name"].tolist())

def nodes_with_largest_memory(nodesDF,nNodes):
    return set(nodesDF.sort_values(by="RAM",ascending=False).head(nNodes)["node_name"].tolist())

def update_apt(nodes): ## update apt
    Remote("apt-get -y update",hosts=nodes,connection_params={'user': 'root'}).run()
    # We could print how the update is going by creating a handler handler = PyConsoleOutputHandler()
    # Remote("apt-get -y update",hosts=nodes,connection_params={'user': 'root'}
    #       , process_args={'stdout_handlers': [handler], 'stderr_handlers': [handler]}).run()

def install_JDK_7(nodes):
    Remote("DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-7-jre -y openjdk-7-jdk",hosts=nodes,connection_params={'user': 'root'}).run()

def install_dstat(nodes):
    Remote("DEBIAN_FRONTEND=noninteractive apt-get install -y dstat",hosts=nodes,connection_params={'user': 'root'}).run()

def kill_all_processes(name,nodes):
    handler = PyConsoleOutputHandler()
    Remote("pkill -f {0}".format(name),hosts=nodes,connection_params={'user': 'root'}
           , process_args={'stdout_handlers': [handler], 'stderr_handlers': [handler]}).run()



if __name__ == '__main__':
    nodes = {'graphene-2.nancy.grid5000.fr',
     'graphene-4.nancy.grid5000.fr',
     'grimoire-4.nancy.grid5000.fr',
     'grisou-39.nancy.grid5000.fr'}