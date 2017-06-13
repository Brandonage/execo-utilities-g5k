from general_util import *
import numpy as np
import json
from aux_utilities.twilio_client import create_twilio_client


def install_dcos_vagrant(nodes):
    install_vagrant(nodes)
    install_virtual_box(nodes)


def install_vagrant(nodes):
    vagrant_deb = "https://releases.hashicorp.com/vagrant/1.9.3/vagrant_1.9.3_x86_64.deb?_ga=1.247726599.1021702478.1489404346"
    Remote("wget {0} -O {1}/vagrant.deb 2>1".format(vagrant_deb, wget_destination), hosts=nodes,
           connection_params={'user': 'root'}).run()  ## download the debian package for vagrant
    Remote("dpkg -i {0}/vagrant.deb".format(wget_destination), hosts=nodes,
           connection_params={'user': 'root'}).run()  # install the package
    Remote("apt-get -fy install zlib1g-dev", hosts=nodes,
           connection_params={'user': 'root'}).run()  # we also install this dependency to be able to use DC/OS vagrant
    Remote("vagrant plugin install vagrant-hostmanager", hosts=nodes,
           connection_params={'user': 'root'}).run()


def install_virtual_box(nodes):
    Remote(
        "echo deb http://download.virtualbox.org/virtualbox/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) contrib >> /etc/apt/sources.list",
        hosts=nodes, connection_params={'user': 'root'}).run()  ## add the line for the debian package
    # add the keys
    Remote("wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | apt-key add -",
           hosts=nodes, connection_params={'user': 'root'}).run()
    Remote("wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | apt-key add -",
           hosts=nodes, connection_params={'user': 'root'}).run()
    update_apt(nodes)
    Remote("apt-get -y install virtualbox-5.1",
           hosts=nodes, connection_params={'user': 'root'}).run()
    Remote("apt-get -y install dkms",
           hosts=nodes, connection_params={'user': 'root'}).run()


def split_dcos_roles(nodesDF, nmasters, npublic_agents, nprivate_agents):
    nbootstrap = 1  # we need a bootstrap node
    nodes = nodesDF['ip'].values
    splits = np.cumsum([nbootstrap, nmasters, npublic_agents, nprivate_agents])[:-1]
    res = np.split(nodes, splits)
    return set(res[0]), set(res[1]), set(res[2]), set(res[3])


def prepare_config_yaml(masters, private_agents, public_agents, dns_resolver, output_file):
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


def install_dcos_cli(nodes):
    """
    Install DCOS in all nodes.
    :param masternode: The nodes where we want to install the cli. Normally all of them
    """
    Remote("curl https://downloads.dcos.io/binaries/cli/linux/x86-64/dcos-1.9/dcos -o dcos && sudo mv dcos " \
           "/usr/local/bin && sudo chmod +x /usr/local/bin/dcos && dcos config set core.dcos_url http://{{{host}}}",
           hosts=nodes).run()


def query_marathon_api(node, request):
    """
    Query the marathon API from a node and 
    :param node: the node from where to do the query
    :param request: the type of request
    """
    p = SshProcess("curl -H \"Authorization: token=$AUTH_TOKEN\" http://leader.mesos:8080/v2/" + request ,host=node)
    p.run()
    print p.stdout
    d = json.loads(p.stdout)
    return d


def install_cassandra(masternode, ncassandra, nseeds):
    replace_infile(pathin="dcos-resources/cassandra-template.json",
                   pathout="dcos-resources/cassandra-config.json",
                   replacements={"@ncassandra@": ncassandra, "@nseeds@": nseeds}
                   )
    Put(hosts=masternode, local_files=["dcos-resources/cassandra-config.json"]).run()
    raw_input("Please install Cassandra Service with the following command:"
              "dcos package install --yes --options=cassandra-config.json cassandra  "
              "A message will be sent when everything is ready: ")
    not_ready = True
    while (not_ready):
        sleep(10)
        p = SshProcess('curl "http://leader.mesos/service/cassandra/v1/plan"',
                       host=masternode
                       )
        p.run()
        print p.stdout
        d = json.loads(p.stdout)
        status = d.get("status")
        if (status=='COMPLETE'):
            not_ready = False
    print "THE CASSANDRA CLUSTER IS READY!!"
    # print "Execute this command in the machine {0}: dcos package install --yes --options=cassandra-config.json cassandra"\
    #     .format(list(masternode))
    # print "And this: dcos package install cassandra --cli"
    # raw_input("After executing press enter: ")
    # r = Remote(cmd="dcos package install --yes --options=cassandra-config.json cassandra",
    #        hosts=masternode,
    #        process_args={'stdout_handlers': [sys.stdout],
    #                      'stderr_handlers': [sys.stderr],
    #                      'shell':True,
    #                      'pty': True
    #                      }).start()
    # r.expect('press RETURN')
    # print "Trying to return interactively"
    # print >>r,"\n"
    # r.wait()
    p = SshProcess(cmd="dcos cassandra --name=cassandra connection",
                   host=masternode)
    p.run()
    print p.stdout
    d = json.loads(p.stdout)
    return set([s.replace(':9042', '') for s in d['address']])  # we remove the port since we will pass this to the YCSB
