##
##  THIS FILE INCLUDES FUNCTIONS THAT RESERVE NODES, DEPLOY ENVIRONMENTS AND INSTALL TOOLS AND SOFTWARE INTO GRID5000
##  TODO MIGRATE EACH RESERVE, DEPLOY AND INSTALL FUNCTIONS TO DIFFERENT FILES
##
##



from execo import *
from execo_g5k import *

# The dict will look like
# {column1:listof(tuples(value,number)),column2:listof(tuples(value,number)),....columnn:listof(tuples(value,number))}
# e.g. {"cluster":[("grimani",2),("grisou",2)],"nodes":[(["graphite1","graphite2","graphite3"],3)]}
# Note: For the nodes column the values of the dict is a listof(tuples(listofnodes,numberofnodes))
def build_resources_query(dict): ## (dict: Dict of resources ) ## It takes a dict of resources and builds a query to be passed to oarsub
    query=""
    for column, listoftuples in dict.iteritems():
        if column=="cluster": ## we expect a list of tuples and build a query like "{cluster='tuple[0]'}/nodes=tuple[1],"
            for tuple in listoftuples:
                query += "{cluster='" + tuple[0] + "'}/nodes=" + str(tuple[1]) + ","
        if column=="nodes": ## we expect a list of tuples and build a query like "{host in ('node1','node2'...'nodeN')}/nodes=tuple[1],"
            for tuple in listoftuples:
                listofnodes = tuple[0]
                string_of_nodes = ""
                for node in listofnodes:
                    string_of_nodes += "'" + node + "',"
                string_of_nodes=string_of_nodes[:-1] ## take out the last comma
                query += "{host in (" + string_of_nodes + ")}/nodes=" + str(tuple[1]) + ","
    query=query[:-1] ## take out the last comma
    return query

## Returns a jobid to be added to the experiment information
def reserve_nodes(frontend,resources,walltime,date,experiment_name): ## {frontend:String, resources: Dict of resources, walltime: String, date: compliance with time package, experiment_name : String}
    ##TODO resources_query
    resources_query=build_resources_query(resources)
    logger.info("oarsub with resources" + resources_query)
    [(jobid, site)] = oarsub([
        ( OarSubmission(resources = resources_query,walltime=walltime,job_type="deploy",reservation_date=date,name=experiment_name), frontend)
    ])
    return jobid

def deploy_nodes(frontend,jobid):
    nodes = []
    wait_oar_job_start(jobid,frontend)
    nodes = get_oar_job_nodes(jobid,frontend)
    deployed, undeployed = deploy(Deployment(nodes, env_name = "wheezy-x64-nfs"),num_tries=3)
    return deployed,undeployed

def clear_reservation(frontend,jobid):
    oardel([(jobid, frontend)])




if __name__ == '__main__':
    dict = {"cluster":[("grimoire",1),("grisou",1)],"nodes":[(["graphene-4.nancy.grid5000.fr","graphene-2.nancy.grid5000.fr"],2)]}
    resources_query = build_resources_query(dict)
    walltime = "2:00:00"
    date=None
    experiment_name="execo_test"
    frontend="nancy"
    [(jobid, site)] = oarsub([
        ( OarSubmission(resources = resources_query,walltime=walltime,job_type="deploy",reservation_date=date,name=experiment_name), frontend)
    ])
    oardel([(jobid, site)])
