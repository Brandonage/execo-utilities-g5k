from utils.general_util import *
import itertools


def start_dstat(nodes):
    Remote("nohup dstat -cdngym --proc --io --ipc --socket --net-packets --proc-count --disk-util --rpc --rpcd --vm --output /opt/GMonE-MC/dstat.csv > /dev/null 2>&1",hosts=nodes,connection_params={'user': g5k_user}
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
    Remote("chown -R {0}:users /opt/GMonE-MC".format(g5k_user),hosts=master.union(slaves),
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
    Remote("apt-get install -y xz-utils".format(tarball_url,wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("wget {0} -O {1}/nodejs.tar.xz".format(tarball_url,wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0} && tar xf nodejs.tar.xz".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0} && mv node-* node".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()
    Remote("cd {0}/node/bin && ./npm install -g slim.js".format(wget_destination),hosts=master,connection_params={'user': 'root'}).run()

def start_slim(master):
    Remote("PATH=$PATH:/opt/node/bin nohup slim -p 27017",hosts=master,connection_params={'user':g5k_user},process_args={"shell":True}).start()


def install_dstat(nodes,os):
    if os=='debian':
        Remote("DEBIAN_FRONTEND=noninteractive apt-get install -y dstat",hosts=nodes,connection_params={'user': 'root'}).run()
    if os=='centos':
        Remote("sudo yum -y install dstat",hosts=nodes).run()

def start_sysdig_network(nodes):
    # cmd = "sudo docker run -i -t --name sysdig --privileged " \
    #       "-v /var/run/docker.sock:/host/var/run/docker.sock -v /dev:/host/dev -v /proc:/host/proc:ro " \
    #       "-v /boot:/host/boot:ro -v /lib/modules:/host/lib/modules:ro -v /usr:/host/usr:ro -v /home/vagrant:/host/vagrant " \
    #       "sysdig/sysdig sysdig \"(fd.type=ipv4 or fd.type=ipv6)\" " \
    #       "and evt.is_io=true -pc\"*%evt.rawtime.s,%fd.type,%evt.type,%evt.args,%evt.dir,%proc.name,%proc.pid,%container.name," \
    #       "%container.image,%container.id,%container.type,%fd.cip,%fd.sip,%fd.cport,%fd.sport,%fd.lport,%fd.rport," \
    #       "%fd.l4proto,%evt.io_dir,%evt.failed,%evt.category,%evt.rawarg.res,\" -w /host/vagrant/{{{host}}}.scrap"
    cmd = "sudo docker run -i -t --name sysdig --privileged " \
          "-v /var/run/docker.sock:/host/var/run/docker.sock -v /dev:/host/dev -v /proc:/host/proc:ro " \
          "-v /boot:/host/boot:ro -v /lib/modules:/host/lib/modules:ro -v /usr:/host/usr:ro -v /home/vagrant:/host/vagrant " \
          "sysdig/sysdig sysdig \"not(proc.name contains stress-ng)\" and \"(fd.type=ipv4 or fd.type=ipv6)\" and evt.is_io=true " \
          "-pc\"%evt.rawtime.s,%fd.num,%fd.type,%evt.type,%evt.dir,%proc.name,%proc.pid,%container.name,%container.image,%container.id,%container.type,%fd.name,%fd.cip,%fd.sip,%fd.lip,%fd.rip,%fd.is_server,%fd.cport,%fd.sport,%fd.lport,%fd.rport,%fd.l4proto,%evt.io_dir,%evt.category,%evt.rawarg.res\" " \
          "-w /host/vagrant/{{{host}}}.scrap"
    Remote(cmd,hosts=nodes).start()

def stop_sysdig(nodes):
    Remote("sudo docker stop sysdig",hosts=nodes).run()
    Remote("sudo docker rm sysdig", hosts=nodes).run()


def start_cadvisor(nodes):
    cmd = "sudo docker run --volume=/:/rootfs:ro --volume=/var/run:/var/run:rw --volume=/sys:/sys:ro " \
          "--volume=/var/lib/docker/:/var/lib/docker:ro --volume=/dev/disk/:/dev/disk:ro --volume=/cgroup:/cgroup:ro " \
          "--publish=8082:8080 --privileged=true --detach=true --name=cadvisor google/cadvisor:latest"
    Remote(cmd,hosts=nodes).start()

def start_node_exporter(nodes):
    cmd = "sudo docker run -it -p 9100:9100 " \
          "-v /proc:/host/proc:ro " \
          "-v /sys:/host/sys:ro " \
          "-v /:/rootfs:ro " \
          "--net=\"host\" " \
          "prom/node-exporter " \
          "--path.procfs=\"/host/proc\" " \
          "--path.sysfs=\"/host/sys\" " \
          "--collector.filesystem.ignored-mount-points=\"^/(sys|proc|dev|host|etc)($|/)\" "
    Remote(cmd,hosts=nodes).start()

def start_prometheus(scrape_nodes,scrape_ports):
    list_of_targets = [ip + ':' + port for (ip, port) in itertools.product(scrape_nodes, scrape_ports)]
    replace_infile(pathin="aux_utilities/prometheus_template.yml",
                   pathout="aux_utilities/prometheus.yml",
                   replacements={"@list_targets@": str(list_of_targets)}
                   )
    Put(hosts='nancy.g5k',
        local_files=["aux_utilities/prometheus.yml"],
        remote_location="/home/abrandon/prometheus/prometheus-1.7.2.linux-amd64",
        connection_params={'user': g5k_configuration.get("g5k_user")}).run() # new configuration for Prometheus
    Remote(cmd="pkill -HUP prometheus",
           hosts='nancy.g5k',
           connection_params={'user': g5k_configuration.get("g5k_user")}).run() # restart the prometheus server

