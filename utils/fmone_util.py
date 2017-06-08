from utils.general_util import *


def build_json_pipeline(type_of_pipeline,replacements):
    # type: (str, dict) -> str
    """
    A function to create the JSON's for different types of pipelines 
    :param type_of_pypeline: A str with the type of pipeline we want to build 
    :param replacements: a dict with the arguments that need to be susbtituted on the template JSON 
    """
    templates = {"aggregate_and_centralise": "fmone-resources/fmoneagg.json",
                 "regional_mongo" : "fmone-resources/regionalmongo.json",
                 "central_mongo": "fmone-resources/centralmongo.json",
                 "central_ycsb" : "fmone-resources/centralycsb.json"}
    try:
        replace_infile(templates[type_of_pipeline],"fmone-resources/exec.json",replacements)
        with open("fmone-resources/exec.json",'r') as f:
            data=f.read()
            print data
            return data
    except KeyError:
        print "Invalid pipeline name. These are the valid options: "
        print templates

def execute_pipeline(type_of_pipeline,replacements,nodes,connection_params):
    # type: (str, dict, set, dict) -> object
    """
    Execute a fmone monitorisation pipeline
    :param type_of_pipeline: the type of pipeline we want to execute
    :param replacements: the parameters a.k.a the values that we are going to replace on the json template
    :param node: the node from where we will curl the json
    :param connection_params: we need the connection parameters from an execo environment. e.g. vagrant, g5k, amazon...
    """
    build_json_pipeline(type_of_pipeline, replacements)
    curl_node = {list(nodes)[0]} # this is the node from where we will perform the curl. It's one of the masters
    Put(hosts=curl_node, local_files=["fmone-resources/exec.json"],
                     remote_location="/home/vagrant/exec.json",connection_params=connection_params).run()
    p = Remote('curl -X POST "http://marathon-user.marathon.mesos:10000/v2/groups" -H "content-type: application/json" ' +
           '-d@/home/vagrant/exec.json',hosts=curl_node,connection_params=connection_params).run()
    print p.processes[0].stdout
    print p.processes[0].stderr





