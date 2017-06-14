from utils.general_util import *
from os.path import expanduser

def install_cassandra(nodes,nseeds,dc_name):
    # type: (set, int, str) -> set
    print "Uploading the rpm to all nodes"
    Put(hosts=nodes,
        local_files=[expanduser("~") + '/vagrant-g5k/resources/cassandra-3.0.13-1.noarch.rpm']
        ).run()
    print "Installing JDK in all nodes"
    install_JDK_8(nodes=nodes, os="centos")
    print "Installing the RPM"
    Remote("sudo rpm -Uvh cassandra-3.0.13-1.noarch.rpm",
           hosts=nodes,
           process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
           ).run()
    seeds = list(nodes)[:nseeds]
    for node in nodes:
        upload_cassandra_yaml(node,seeds,dc_name)
    # we first initialise the seeds
    for seed in seeds:
        Remote("sudo service cassandra start",
           hosts={seed},
           process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
           ).run()
        print "Started seed node {0}".format(seed)
        sleep(10)
    # and then the rest
    for node in nodes.difference(set(seeds)):
        Remote("sudo service cassandra start",
           hosts=node,
           process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
           ).run()
        print "Started node {0}".format(node)
        sleep(30)
    return nodes

def upload_cassandra_yaml(node,seeds,dc_name):
    replace_infile(pathin="aux_utilities/cassandra_template.yaml",
                   pathout="aux_utilities/cassandra.yaml",
                   replacements={"@clustername@":dc_name,
                                 "@seeds@":",".join(list(seeds)),
                                 "@host_ip@": node})
    Put(hosts=node,
        local_files=["aux_utilities/cassandra.yaml"]
        ).run()
    Remote("sudo cp cassandra.yaml /etc/cassandra/conf",
           hosts=node,
           process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
           ).run()

