from general_util import *


def start_dstat(nodes):
    Remote("nohup dstat -cdngym --proc --io --ipc --socket --net-packets --proc-count --disk-util --rpc --rpcd --vm --output /opt/GMonE-MC/dstat.csv > /dev/null 2>&1",hosts=nodes,connection_params={'user': 'abrandon'}
           ,process_args={"shell":True}).start()

##Upload the GMone directory in gmone-resources/GMonE-MC to all the nodes
def install_gmone(master,slaves):
    #   We put the GMONE source code in the machines
    Put(hosts=master.union(slaves),local_files=["gmone-resources/GMonE-MC"],remote_location="/opt",connection_params={'user': 'root'}).run()
    #   prepare the templates/manager.conf.template file with all the nodemanagers that the master is going to subscribe to
    replace_infile(pathin="gmone-resources/templates/manager.conf.template",pathout="gmone-resources/tmp/manager.conf",replacements={"@slavenodes@":",".join(list(slaves))})
    #   and upload to all nodes
    Put(hosts=master.union(slaves),local_files=["gmone-resources/tmp/manager.conf"],remote_location="/opt/GMonE-MC/manager.conf"
        ,connection_params={'user': 'root'}).run()
    #   upload the templates/monitor.conf.template to all nodes. This file have all the metrics that the monitors are going to send to the master
    Put(hosts=master.union(slaves),local_files=["gmone-resources/templates/monitor.conf.template"],remote_location="/opt/GMonE-MC/monitor.conf"
        ,connection_params={'user': 'root'}).run()
    #   change permissions so g5k_user can operate with GMONE
    Remote("chown -R {0}:users /opt/GMonE-MC".format(g5k_configuration.get("g5k_user")),hosts=master.union(slaves),
           connection_params={'user': 'root'}).run()

def start_gmonedb(master):
    Remote("cd /opt/GMonE-MC/ && nohup /opt/GMonE-MC/gmonedb.sh {{{host}}} /opt/GMonE-MC/manager.conf > /dev/null 2>&1",hosts=master,
           connection_params={'user':g5k_configuration.get('g5k_user')},process_args={"shell":True}).start()

def start_gmonemon(slaves):
    start_dstat(slaves)
    Remote("cd /opt/GMonE-MC/ && nohup /opt/GMonE-MC/gmonemon.sh {{{host}}} /opt/GMonE-MC/monitor.conf > /dev/null 2>&1",hosts=slaves,
           connection_params={'user':g5k_configuration.get('g5k_user')},process_args={"shell":True}).start()
    #Remote(cmd,hosts="griffon-8.nancy.grid5000.fr",connection_params={'user':g5k_configuration.get('g5k_user')},
    #process_args={"shell":True,'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]})

def start_gmone(master,slaves):
    start_gmonemon(slaves)
    start_gmonedb(master)

def install_slim(master):
    tarball_url = "https://nodejs.org/dist/v4.4.3/node-v4.4.3-linux-x64.tar.xz"
    Remote("wget {0} -O {1}/nodejs.tar.xz".format(tarball_url,wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0} && tar xf nodejs.tar.xz".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0} && mv node-* node".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0}/node/bin && ./npm install -g slim.js".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()

def start_slim(master):
    Remote("PATH=$PATH:/opt/node/bin nohup slim -p 27017",hosts=master,connection_params={'user':g5k_configuration.get('g5k_user')},process_args={"shell":True}).start()


