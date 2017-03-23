from general_util import *

#   TODO: Implement the logic to choose the masternodes and slaves of mesos

mesos_home = "/opt/mesos"
mesos_build = mesos_home + "/build"
mesos_conf = "/usr/local/etc/mesos"
tarball_url  = "http://www.apache.org/dist/mesos/1.1.0/mesos-1.1.0.tar.gz"

def install_mesos_dependecies(nodes):
    Remote("DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential python-dev libcurl4-nss-dev libsasl2-dev libsasl2-modules maven libapr1-dev libsvn-dev zlib1g-dev",
           hosts=nodes,connection_params={'user': 'root'}).run() ## Install some dependencies of Mesos
    Remote("DEBIAN_FRONTEND=noninteractive apt-get -y install g++", ## Install c++ compiler
           hosts=nodes,connection_params={'user': 'root'}).run()

def build_and_install_mesos(nodes):
    install_mesos_dependecies(nodes)
    Remote("wget {url} -O {destination}/mesos.tar.gz".format(url=tarball_url,destination=wget_destination),
           hosts=nodes,connection_params={'user': 'root'}).run() ## Download the mesos distribution on it
    Remote("cd {0} && tar -xvzf mesos.tar.gz".format(wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() ## untar Mesos
    Remote("cd {0} && mv mesos-* mesos".format(wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() ## move mesos to a new directory without the version name
    Remote("mkdir " + mesos_build,hosts=nodes, connection_params={'user': 'root'}).run() ## create the directory for mesos build
    Remote("cd {0} && ../configure".format(mesos_build), hosts=nodes, connection_params={'user': 'root'},
           process_args=output_handler_args).run()
    Remote("cd {0} && make -j 8".format(mesos_build), hosts=nodes, connection_params={'user': 'root'},
           process_args=output_handler_args).run()
    Remote("cd {0} && make check -j 8".format(mesos_build), hosts=nodes, connection_params={'user': 'root'},
           process_args=output_handler_args).run()
    Remote("cd {0} && make install".format(mesos_build), hosts=nodes, connection_params={'user': 'root'},
           process_args=output_handler_args).run()
    #   We decide to execute and install the service as root to not complicate things. There are problems when installing
    #   the dependencies of Mesos as a normal user
    #Remote("chown -R {0}:users {1}*".format(g5k_user,mesos_home),hosts=masternode,connection_params={'user': 'root'}).run()
    Remote("mkdir /var/lib/mesos",hosts=nodes,connection_params={'user': 'root'}).run()
    #Remote("chown -R {0}:users /var/lib/mesos".format(g5k_user),hosts=masternode,connection_params={'user': 'root'}).run()

def copy_mesos_from_home(masternode):
    pass    ## When we have a compiled version of mesos we can just copy it to the opt folder


def configure_mesos(masternode, masters, slaves, osMemory):
    """

    :param masternode: the node used for bootstraping
    :param masters: the nodes that are going to act as masters in mesos
    :param slaves: the nodes that are going to act as slaves in mesos
    :param osMemory: still not used. Can change options on the mesos-deploy-env.sh script to launch with mem limits
    """
    agent_template = "mesos-resources/mesos-agent-env.template.sh"
    agent_template_out = "mesos-resources/mesos-agent-env.sh"
    master_template = "mesos-resources/mesos-master-env.template.sh"
    master_template_out = "mesos-resources/mesos-master-env.sh"
    ## Build the masters and slaves files (Not really useful since we will start the mesos cluster with execo remote tasks)
    with open("mesos-resources/slaves","w") as f:
        for node in slaves:
            f.write(node + "\n")
    with open("mesos-resources/masters","w") as f:
        for node in masters:
            f.write(node + "\n")
    Put(hosts=masternode,local_files=["mesos-resources/slaves"],
        remote_location=mesos_conf + "/slaves",connection_params={'user': 'root'}).run()
    Put(hosts=masternode,local_files=["mesos-resources/masters"],
        remote_location=mesos_conf + "/masters",connection_params={'user': 'root'}).run()
    ## build the agent-env.sh file #TODO I think we will have to put the IP's here not the names
    replace_infile(pathin=agent_template,pathout=agent_template_out,replacements={"@masternode@":list(masters)[0]})
    Put(hosts=slaves,local_files=[agent_template_out],remote_location=mesos_conf + "/mesos-agent-env.sh",
        connection_params={'user': 'root'}).run()
    ## build the master-env.sh file
    #   no need to replace anything YET
    #replace_infile(pathin=master_template,pathout=master_template_out,replacements={"@namenode@":list(masters)[0]})
    Put(hosts=masters,local_files=[master_template_out],remote_location=mesos_conf + "/mesos-master-env.sh",
        connection_params={'user': 'root'}).run() ## we upload core_site.xml to all hosts
    # Put(hosts=masternode,local_files=["mesos-resources/mesos-deploy-env.sh"],
    #    remote_location=mesos_conf + "/masters",connection_params={'user': 'root'}).run()

def start_mesos(masters,slaves):
    Remote("ldconfig",hosts=masters,connection_params={'user': 'root'}).run() # rebuild the cache of shared libraries
    Remote("/usr/local/sbin/mesos-daemon.sh mesos-master </dev/null >/dev/null",hosts=masters,connection_params={'user': 'root'}).run()
    Remote("/usr/local/sbin/mesos-daemon.sh mesos-agent </dev/null >/dev/null",hosts=slaves,connection_params={'user': 'root'}).run()


def stop_mesos(masternode):
    Remote("/usr/local/sbin/mesos-stop-cluster.sh".format(mesos_build),hosts=masternode,connection_params={'user': 'root'}).run()




