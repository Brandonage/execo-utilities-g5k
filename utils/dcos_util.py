from general_util import *
from general_util import wget_destination, update_apt
import numpy as np


def install_dcos_vagrant(nodes):
    install_vagrant(nodes)
    install_virtual_box(nodes)


def install_vagrant(nodes):
    vagrant_deb = "https://releases.hashicorp.com/vagrant/1.9.3/vagrant_1.9.3_x86_64.deb?_ga=1.247726599.1021702478.1489404346"
    Remote("wget {0} -O {1}/vagrant.deb 2>1".format(vagrant_deb,wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() ## download the debian package for vagrant
    Remote("dpkg -i {0}/vagrant.deb".format(wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() # install the package
    Remote("apt-get -fy install zlib1g-dev",hosts=nodes,
           connection_params={'user': 'root'}).run() # we also install this dependency to be able to use DC/OS vagrant
    Remote("vagrant plugin install vagrant-hostmanager",hosts=nodes,
           connection_params={'user': 'root'}).run()


def install_virtual_box(nodes):
    Remote("echo deb http://download.virtualbox.org/virtualbox/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) contrib >> /etc/apt/sources.list",
           hosts=nodes,connection_params={'user': 'root'}).run() ## add the line for the debian package
    # add the keys
    Remote("wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | apt-key add -",
           hosts=nodes,connection_params={'user': 'root'}).run()
    Remote("wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | apt-key add -",
           hosts=nodes,connection_params={'user': 'root'}).run()
    update_apt(nodes)
    Remote("apt-get -y install virtualbox-5.1",
           hosts=nodes,connection_params={'user': 'root'}).run()
    Remote("apt-get -y install dkms",
           hosts=nodes,connection_params={'user': 'root'}).run()

def split_dcos_roles(nodesDF,nmasters,npublic_agents,nprivate_agents):
    nbootstrap = 1 # we need a bootstrap node
    nodes = nodesDF['ip'].values
    splits = np.cumsum([nbootstrap,nmasters,npublic_agents,nprivate_agents])[:-1]
    res = np.split(nodes, splits)
    return set(res[0]), set(res[1]), set(res[2]), set(res[3])

def prepare_config_yaml(masters,private_agents,public_agents,dns_resolver,output_file):
    str_priv_agent = '- ' + '\n- '.join(list(private_agents)) + '\n'
    str_pub_agent = '- ' + '\n- '.join(list(public_agents)) + '\n'
    str_master_agent = '- ' + '\n- '.join(list(masters)) + '\n'
    str_dns = '- ' + '\n- '.join(list(dns_resolver)) + '\n'
    replace_infile(pathin="dcos-resources/config_template.yaml",
                   pathout=output_file,
                   replacements={"@agent_list@": str_priv_agent,
                                 "@master_list@": str_master_agent,
                                 "@public_agent_list@": str_pub_agent,
                                 "@resolvers_list@": str_dns})


def restart_dcos_mesos_slave(slaves):
    Remote("systemctl stop dcos-mesos-slave",
                        hosts=slaves).run()
    Remote("rm -f /var/lib/mesos/slave/meta/slaves/latest",
                        hosts=slaves).run()
    Remote("systemctl start dcos-mesos-slave",
                        hosts=slaves).run()

