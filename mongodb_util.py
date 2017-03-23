from general_util import *

#   Install mongodb on one node. Normally the master node in a spark topology
def install_and_run_mongodb(node):
    Remote("apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6",hosts=node,connection_params={'user': 'root'}).run()
    Remote("echo deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main | tee /etc/apt/sources.list.d/mongodb-org-3.4.list",hosts=node,connection_params={'user': 'root'}).run()
    Remote("apt-get update",hosts=node,connection_params={'user': 'root'}).run()
    Remote("apt-get install -y mongodb-org",hosts=node,connection_params={'user': 'root'}).run()
    Remote("service mongod start",hosts=node,connection_params={'user': 'root'}).run()


def export_mongodb(node, database, collection, out_path):
    Remote("mongoexport -d {0} -c {1} --out {2}".format(database,collection,out_path),hosts=node,connection_params={'user': g5k_user}).run()