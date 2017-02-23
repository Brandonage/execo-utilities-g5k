from general_util import *

#   Install mongodb on one node. Normally the master node in a spark topology
def install_and_run_mongodb(node):
    Remote("apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10",hosts=node,connection_params={'user': 'root'}).run()
    Remote("echo deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list",hosts=node,connection_params={'user': 'root'}).run()
    Remote("apt-get update",hosts=node,connection_params={'user': 'root'}).run()
    Remote("apt-get install -y mongodb-org",hosts=node,connection_params={'user': 'root'}).run()

def export_mongodb(node, database, collection, out_path):
    Remote("mongoexport -d {0} -c {1} --out {2}".format(database,collection,out_path),hosts=node,connection_params={'user': g5k_configuration.get("g5k_user")}).run()