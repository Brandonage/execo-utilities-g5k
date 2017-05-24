##
##  THIS FILE WILL INCLUDE UTILITIES THAT WILL BE USED BY EXTERNAL AND INTERNAL SCRIPTS
##
##
##
from execo import *
from execo_g5k import *
from jsonpath_rw import parse
from numpy import mean, nan, array, split, cumsum
from pandas import DataFrame
from common.custom_output_handler import PyConsoleOutputHandler
import warnings

bytes_in_gigabyte = 1073741824  ## The number of bytes in one gigabyte
bytes_in_megabyte = 1048576
wget_destination = "/opt"  ## This is where we are going to untar all the wget files
g5k_user = g5k_configuration.get("g5k_user")
handler = PyConsoleOutputHandler()  ## we can use this object if we want to track the output and errors of the processes
output_handler_args = {'stdout_handlers': [handler], 'stderr_handlers': [handler]}


## (node_dict : Dict with the JSON of querying the Grid5k API, resource: String, the name of the resource)
## RETURNS: A representation in int,boolean or unique values of that resource for the node
## (We use the jsonpath library to add the path inside the JSON of each resource)
def get_resource(node_dict, resource):
    parse_dict = {  ## We start by creating parsers that will extract the information from the JSON structure
        "power_available": "sensors.power.available",
        "node_flops": "performance.node_flops",
        "CPU description": "processor.other_description",
        "PDU": "sensors.power.via.pdu[*].uid",
        "GPU": "gpu.gpu",
        "SSD": "storage_devices[*].storage",
        "HDD": "storage_devices[*].storage",
        "storage_size": "storage_devices[*].size",
        "RAM": "main_memory.ram_size",
        "cores": "architecture.nb_cores",
    }
    jsonpath_expr = parse(parse_dict.get(resource))
    list_of_results = [match for match in
                       jsonpath_expr.find(node_dict)]  ## Get a list of data from the JSON that matches that pattern
    if len(list_of_results) == 0:
        return ""
    else:  # Different resources will have different formats in their JSON values. We give them a readable format through this logic
        if (resource in ["power_available", "node_flops", "CPU description", "GPU",
                         "cores"]):  ##if the resource has a unique value
            return list_of_results[0].value  ##return the single value
        if (resource == "PDU"):
            values = [res.value for res in list_of_results]  ## get the values of the list of one element
            return ' and '.join(values)  ## We want a string with the different PDU's
        if (resource in ["SSD", "HDD"]):
            values = [res.value for res in list_of_results if
                      res.value == resource]  ## We get a list with the different types of storage that node has (e.g. SSD, HDD)
            capacity = [res.context.value.get("size") for res in list_of_results if
                        res.value == resource]  ## We get a list with the size of storage for each disk of that type
            if values:  ## If we have values
                return str(values.count(resource)) + " * " + str(int(mean(
                    capacity) / bytes_in_gigabyte)) + " GB"  ## We want the number of SSD's disk on the node and the mean capacity of this number
            else:  ## If not return empty string
                return nan
        if (resource in ["storage_size", "RAM"]):
            values = [res.value for res in list_of_results]
            return sum(values) / bytes_in_gigabyte  ## We want the sum of all the storage in that node


##(nodes:A list of nodes that are returned by the get_oar_job_nodes(jobid,site) function)
## It will return a Pandas Dataframe with the network, disk, CPU and other resources for the different nodes.
## This will allow us to order the Dataframe by CPU speed, disk and so on
def build_dataframe_of_nodes(nodes):
    d = {}  ## we will build the dataframe with this dictionary
    resources = ["power_available", "node_flops", "CPU description", "PDU", "GPU", "SSD", "HDD", "storage_size", "RAM",
                 "cores"]  ## This is a list of the resources we want to query
    list_of_nodes_dict = [get_host_attributes(node) for node in nodes]  ## get the information of the list of nodes
    for resource in resources:  ## For each resource
        values = [get_resource(node_dict, resource) for node_dict in
                  list_of_nodes_dict]  ## Get a list of the values for that resource
        d.update({resource: values})  # update the list
    d.update({"node_name": list(
        nodes)})  ## We need three additional fields that are outside the list of dictionaries. First the name of nodes
    d.update({"cluster": [get_host_cluster(node) for node in nodes]})  ## The name of the cluster
    d.update({"site": [get_host_site(node) for node in nodes]})
    return DataFrame(d)


def replace_infile(pathin, pathout, replacements):
    """
    it replaces all the occurences of a word for another one included in a dictionary
    :param pathin: the path for the input file
    :param pathout: the path where the output file will be copied
    :param replacements: a dictionary with the replacements we want to make e.g. replacements={"@namenode@":"paravance-5.grid5000.fr"}
    """
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
def nodes_with_largest_storage(nodesDF, nNodes):
    return set(nodesDF.sort_values(by="storage_size", ascending=False).head(nNodes)["node_name"].tolist())


def nodes_with_largest_memory(nodesDF, nNodes):
    return set(nodesDF.sort_values(by="RAM", ascending=False).head(nNodes)["node_name"].tolist())


def install_general_utils(nodes):
    Remote("apt-get -y install git", hosts=nodes, connection_params={'user': 'root'}).run()
    Remote("apt-get -y install screen", hosts=nodes, connection_params={'user': 'root'}).run()
    #   We also add sudo TODO:Add the user g5k_user to sudo
    Remote("apt-get -y install sudo", hosts=nodes, connection_params={'user': 'root'}).run()
    #   We add lsb-release package since its handy for mesosphere install scripts
    #   http://serverfault.com/questions/476485/do-some-debian-builds-not-have-lsb-release
    Remote("apt-get install lsb-release", hosts=nodes, connection_params={'user': 'root'}).run()
    # We could print how the update is going by creating a handler handler = PyConsoleOutputHandler()
    # Remote("apt-get -y update",hosts=nodes,connection_params={'user': 'root'}
    #       , process_args={'stdout_handlers': [handler], 'stderr_handlers': [handler]}).run()


def update_apt(nodes):  ## update apt
    Remote("apt-get -y update", hosts=nodes, connection_params={'user': 'root'}).run()
    #   We add the screen package which is not installed by default


def install_JDK_7(nodes):
    Remote("DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-7-jre -y openjdk-7-jdk", hosts=nodes,
           connection_params={'user': 'root'}).run()


def install_JDK_8(nodes):
    #   We need backports with the jessie distribution
    Remote("apt install -yt jessie-backports  openjdk-8-jre-headless ca-certificates-java", hosts=nodes,
           connection_params={'user': 'root'}).run()
    Remote("DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jre -y openjdk-8-jdk", hosts=nodes,
           connection_params={'user': 'root'}).run()
    #   We need to update the path to the 8 version
    Remote("update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java", hosts=nodes,
           connection_params={'user': 'root'}).run()


def kill_all_processes(name, nodes):
    handler = PyConsoleOutputHandler()
    Remote("pkill -f {0}".format(name), hosts=nodes, connection_params={'user': 'root'}
           , process_args={'stdout_handlers': [handler], 'stderr_handlers': [handler]}).run()


def get_dns_server(node):
    p = SshProcess("cat /etc/resolv.conf | grep nameserver", node)
    p.run()
    return {p.stdout.split(' ')[1].replace('\r\n', '')} # some preprocessing we need to eliminate strange symbols


def divide_nodes_into_regions(proportions, nodes):
    """
    a function that splits a series of nodes into regions of different sizes
    it returns a list of list with each element being the nodes of that region
    :rtype: list
    :param proportions: a list with the proportions for each region
    :param nodes: a complete list of nodes that constitute the cluster
    """

    def splitPerc(l, perc):
        splits = cumsum(perc) / 100.
        if splits[-1] != 1:
            warnings.warn("The percentages don't add up to 1", UserWarning)
        return split(l, (splits[:-1] * len(l)).astype(int))

    percents = array(proportions)
    return map(set, splitPerc(nodes, percents))


def limit_bandwith_qdisc(nodes, netem_idx, cap_rate="86Mbit"):
    Remote(
        "sudo tc qdisc add dev eth0 root handle 1: htb", hosts=nodes
    ).run()
    # sudo tc qdisc add dev eth0 root handle 1: htb
    Remote(
        "sudo tc class add dev eth0 parent 1: classid 1:{0} htb rate {1}"
            .format(netem_idx, cap_rate), hosts=nodes
    ).run()
    # sudo tc class add dev eth0 parent 1: classid 1:netem_idx htb rate cap_rate


def create_delay_qdisc(nodes, netem_idx, delay="100ms", jitter="0.1ms", packet_loss="0.1%"):
    Remote(
        "sudo tc qdisc add dev eth0 parent 1:{0} handle {0}: netem delay {1} {2} 25% loss {3}"
            .format(netem_idx, delay, jitter, packet_loss), hosts=nodes
    ).run()
    # sudo tc qdisc add dev eth0 parent 1:netem_idx handle netem_idx: netem delay delay jitter 25% loss packet_loss
    pass


def add_delay_between_regions(source_region, dest_region, netem_idx):
    # type: (set, set, str) -> None
    """
    Adds delays between regions of nodes
    :param source_region: a set that is going to be the nodes of the source region
    :param dest_region: a set that is going to be the nodes of the destination region 
    :param netem_idx: a netem index for the tc tool
    """
    for node in list(dest_region):
        add_delay_between_nodes(nodes=source_region, node_dest=node, netem_idx=netem_idx)


def add_delay_between_nodes(nodes, node_dest, netem_idx):
    """
    Addes delay between all the nodes of nodes and the SINGLE destination node node_dest
    :param nodes: a set of nodes where we will insert delays to node_dest in parallel
    :param node_dest: the destination node
    :param netem_idx: an index for netem destination
    """
    Remote("sudo tc filter add dev eth0 parent 1: protocol ip u32 match ip dst {0} flowid 1:{1}"
           .format(node_dest, netem_idx), hosts=nodes).run()
    # sudo tc filter add dev eth0 parent 1: protocol ip u32 match ip dst node_dest flowid 1:netem_idx
    pass
