from utils import dcos_util, fmone_util, cassandra_util, general_util
from experiments.vagrantexperiment import VagrantExperiment
from os.path import exists, expanduser
from os import makedirs
from itertools import permutations
import sys
import warnings
from time import strftime, sleep, mktime, strptime, time
import json
from distutils.dir_util import copy_tree
from shutil import rmtree
from glob import glob
from numpy import mean, std
import pandas as pd
# we need to extend the syspath so when we upload the experiment to G5K, it would be able
# to import the YCSB benchmark
sys.path.extend(["/home/abrandon/execo-g5k-benchmarks/ycsb"])
# This shows an error because it doesn't considers the sys.path.extend above
# If we add it to Pycharm we have a problem with the common package which is the same for the benchmarks and the
# execo utilities
from ycsb.cassandraycsb import CassandraYCSB


class FmoneVagrantExperiment(VagrantExperiment):
    masters = None
    public_agents = None
    private_agents = None
    bootstrap = None
    dns_resolver = None

    def __init__(self, frontend, resources, walltime, experiment_name, description, nmasters, nprivate_agents,
                 npublic_agents, vagrantg5k_path=expanduser("~") + "/vagrant-g5k/"):  # default vagrantg5k path
        VagrantExperiment.__init__(self, frontend, resources, walltime, experiment_name, description, vagrantg5k_path)
        self.nmasters = nmasters
        self.npublic_agents = npublic_agents
        self.nprivate_agents = nprivate_agents
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        dcos_util.default_connection_params['user'] = 'vagrant'
        dcos_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        cassandra_util.default_connection_params['user'] = 'vagrant'
        cassandra_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

    def reload_keys(self):
        """
        Use it to reload the execo connection parameters with the ssh vagrant keys and the vagrant user
        """
        general_util.default_connection_params['user'] = 'vagrant'
        general_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        dcos_util.default_connection_params['user'] = 'vagrant'
        dcos_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"
        cassandra_util.default_connection_params['user'] = 'vagrant'
        cassandra_util.default_connection_params['keyfile'] = expanduser("~") + "/.vagrant.d/insecure_private_key"

    def reserve_nodes(self):
        nbootstrap = 1
        # before calling vagrant up lets check if the number of agents and masters equals the nodes specified
        if (sum([r[0] for r in self.resources])) != (
                            nbootstrap + self.nmasters + self.npublic_agents + self.nprivate_agents):
            raise ValueError("The number of VM's is not the same as bootstrap + masters + publicagents + privateagents")
        else:
            VagrantExperiment.reserve_nodes(self)

    def split_dcos_roles(self):
        # First, split the roles
        self.bootstrap, self.masters, self.public_agents, self.private_agents = dcos_util.split_dcos_roles(
            self.nodesDF, self.nmasters, self.npublic_agents, self.nprivate_agents
        )

    def install(self):
        # TODO: THIS SHOULD ALL GO INTO THE DCOS_UTIL FILE AS A FUNCTION "INSTALL DCOS"
        # E.G INSTALL_DCOS(NODESDF,NMASTERS,NPAGENTS,NPRIVAGENTS)
        # We need the dns resolver that the nodes use
        self.dns_resolver = general_util.get_dns_server(self.nodesDF.head(1)['ip'][0])
        # We call the method from dcos_util that installs everything
        dcos_util.install_dcos(self.bootstrap,self.masters,self.public_agents,self.private_agents,self.dns_resolver)


    def build_regions(self, proportions, central_region):
        # we divide the nodes into regions without considering what it will be the master region
        """
        The vagrant experiment has the ability to split its private agents into regions
        :param proportions: the proportions in which we want to split the private_nodes
        :param central_region: the machine that is going to act as central region. It is going to normally hold
        the Marathon user service and all the centralised cloud services
        """
        # We build the regions without considering the central region
        self.regions = general_util.divide_nodes_into_regions(proportions,
                                                              list(self.private_agents.difference(central_region))
                                                              )
        self.central_region = central_region
        # we now include the central region
        self.regions.append(central_region)
        for i in xrange(len(self.regions)):
            if i == (len(self.regions) - 1):
                region_name = "regioncentral"
            else:
                region_name = "region" + str(i)
            with open("mesos-slave-common", "w") as f:
                f.write("MESOS_ATTRIBUTES=region:{0}".format(region_name))
            # it's not possible to ssh as root into a guest VM. We will copy the file to home and then sudo cp
            general_util.Put(hosts=self.regions[i], local_files=["mesos-slave-common"],
                             remote_location="/home/vagrant").run()
            general_util.Remote("sudo cp /home/vagrant/mesos-slave-common /var/lib/dcos/mesos-slave-common",
                                hosts=self.regions[i]).run()
            # we reinitialise the slaves for the attributes to be taken into account
            general_util.Remote("sudo systemctl stop dcos-mesos-slave",
                                hosts=self.regions[i]).run()
            general_util.Remote("sudo rm -f /var/lib/mesos/slave/meta/slaves/latest",
                                hosts=self.regions[i]).run()
            general_util.Remote("sudo systemctl start dcos-mesos-slave",
                                hosts=self.regions[i]).run()
            print "The region {0} has the nodes: {1}".format(region_name, self.regions[i])

    def install_cassandra_dcos(self, ncassandra, nseeds):
        master = list(self.masters)[0]
        # print "Execute this command in the machine {0}: dcos package install --yes --options=cassandra-config.json cassandra" \
        #     .format(master_name)
        # print "And this: dcos package install cassandra --cli"
        # raw_input("After executing press enter: ")
        self.cassandra_nodes = dcos_util.install_cassandra(masternode=master, ncassandra=ncassandra,
                                                           nseeds=nseeds)
        general_util.Put(local_files=["aux_utilities/ycsb_init.cql"],
                         hosts=self.cassandra_nodes).run()
        general_util.Remote(
            cmd="sudo docker run -v /home/vagrant:/home/vagrant cassandra:3.10 cqlsh -f /home/vagrant/ycsb_init.cql {{{host}}}",
            hosts=list(self.cassandra_nodes)[0],
            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
        ).run()

    def install_cassandra(self, ncassandra, nseeds):
        """
        install cassandra natively and spread the cassandra nodes in the central region
        :param ncassandra: the number of nodes
        :param nseeds: the number of seeds
        """
        # sample = int(ncassandra)/self.regions.__len__()
        # cassandra_nodes = []
        # for region in self.regions:
        #     cassandra_nodes.extend(list(region)[:sample])
        self.cassandra_nodes = cassandra_util.install_cassandra(nodes=set(self.central_region),
                                                                nseeds=int(nseeds),
                                                                dc_name="central_test")
        general_util.Put(local_files=["aux_utilities/ycsb_init.cql"],
                         hosts=self.cassandra_nodes).run()
        general_util.Remote(
            cmd="sudo docker run -v /home/vagrant:/home/vagrant cassandra:3.10 cqlsh -f /home/vagrant/ycsb_init.cql {{{host}}}",
            hosts=list(self.cassandra_nodes)[0],
            process_args={'stdout_handlers': [sys.stdout], 'stderr_handlers': [sys.stderr]}
        ).run()

    def ycsb_install(self):
        # We will install yscb only in one node per region
        # nodes_to_install = set([list(region)[0] for region in self.regions])
        regions_to_install = filter(lambda r: not r.issubset(self.central_region), self.regions)
        nodes_to_install = set.union(*regions_to_install)
        # we move the ycsb benchmark that we rsynced to home in order for the CassandraYCSB class to take care of all
        #  the installation process
        print "Uploading the YCSB tar"
        general_util.Put(local_files=[expanduser("~") + "/vagrant-g5k/resources/ycsb-0.12.0.tar.gz"],
                         hosts=nodes_to_install).run()
        general_util.install_JDK_8(nodes_to_install, os="centos")
        self.cassandra_ycsb = CassandraYCSB(install_nodes=nodes_to_install,
                                            execo_conn_params=general_util.default_connection_params,  # needed by execo
                                            cassandra_nodes=self.cassandra_nodes)  # the nodes where cassandra is installed

    def ycsb_install_regions(self, regions):
        # we move the ycsb benchmark that we rsynced to home in order for the CassandraYCSB class to take care of all
        #  the installation process
        print "Uploading the YCSB tar"
        general_util.Put(local_files=[expanduser("~") + "/vagrant-g5k/resources/ycsb-0.12.0.tar.gz"],
                         hosts=regions).run()
        general_util.install_JDK_8(regions, os="centos")
        self.cassandra_ycsb = CassandraYCSB(install_nodes=regions,
                                            execo_conn_params=general_util.default_connection_params,  # needed by execo
                                            cassandra_nodes=self.cassandra_nodes)  # the nodes where cassandra is installed

    def ycsb_run(self, iterations, res_dir, workloads, recordcount, threadcount, fieldlength, target):
        # we build a list of single elements sets with the nodes that will run the yscb workload
        """
        Run a series of workloads a number of iterations and save the results in a directory
        :param iterations: the number of times to execute each workload
        :param res_dir: the directory in which to store the results
        :param workloads: the different workloads that we want to execute
        :param recordcount: the number of records that will be inserted
        :param threadcount: the number of threads for each client
        """
        yscb_clients = self.cassandra_ycsb.install_nodes
        # create a directory for the results
        general_util.Remote(cmd="mkdir results", hosts=yscb_clients).run()
        general_util.Remote(cmd="mkdir results/" + res_dir, hosts=yscb_clients).run()
        for workload in workloads:
            self.cassandra_ycsb.load_workload(from_node=yscb_clients,
                                              workload=workload,
                                              recordcount=recordcount,
                                              threadcount=threadcount,
                                              fieldlength=fieldlength)
            for i in range(iterations):
                self.cassandra_ycsb.run_workload(iteration=i,
                                                 res_dir="results/" + res_dir,
                                                 from_node=yscb_clients,
                                                 workload=workload,
                                                 recordcount=recordcount,
                                                 threadcount=threadcount,
                                                 fieldlength=fieldlength,
                                                 target=target)

    def add_delay(self, delay, bandwidth):
        general_util.limit_bandwith_qdisc(nodes=self.private_agents, netem_idx="10", cap_rate=bandwidth)
        general_util.create_delay_qdisc(nodes=self.private_agents,
                                        netem_idx="10",
                                        delay=delay,
                                        jitter="0.1ms",
                                        packet_loss="0.5%")
        for (orig_region, dest_region) in permutations(self.regions, 2):
            general_util.add_delay_between_regions(orig_region, dest_region, netem_idx="10")

    def run_fmone_pipeline(self, pipeline_type, slaves, region):
        fmone_util.execute_pipeline(pipeline_type,
                                    {"@nslaves@": slaves, "@region@": region},
                                    self.masters, general_util.default_connection_params)

    def save_results(self):
        VagrantExperiment.save_results(self)
        yscb_clients = self.cassandra_ycsb.install_nodes
        general_util.Get(hosts=yscb_clients,
                         remote_files=["results"],
                         local_location=self.results_directory).run()
        copy_tree(".netcheck", self.results_directory)
        rmtree(".netcheck")

    def analyse_results(self, workloads):
        directories = [folder for folder in glob(self.results_directory + '/results/*')]
        results = {}
        for d in directories:
            for w in workloads:
                list_of_metrics, metrics_mean, metrics_var = self.cassandra_ycsb.analyse_results(
                    directory=d,
                    workload=w,
                    metric="Throughput")
                results[w + d] = (list_of_metrics, metrics_mean, metrics_var)
                print "For workload {0} and {1} the mean throughput is: {2} and variance is {3}".format(w, d,
                                                                                                        metrics_mean,
                                                                                                        metrics_var)

    def remove_node(self, node):
        """
        Use this method to remove a node from the experiment
        """
        i = 0
        for set_nodes in self.regions:  # for each region
            if node in set_nodes:  # if the node is in the region
                self.regions[i].remove(node)  # we remove it
                region = self.regions[i]  # and we save the region to find a replacement for the substituted one
            i = i + 1
        try:
            self.nodesDF = self.nodesDF[self.nodesDF['ip'] != node]
            self.nodes.remove(node)
            self.private_agents.remove(node)
            self.cassandra_nodes.remove(node)
            self.cassandra_ycsb.install_nodes.remove(node)
            substitute = list(region)[0]
            self.cassandra_ycsb.install_nodes.add(substitute)
            print "Substituted {0} by {1}. Please install YCSB in this node"
        except AttributeError:
            warnings.warn("There were some attributes missing. Removing node in all possible parts of experiment",
                          UserWarning)

    def checkpoint_network(self):
        """
        This method will export to a temporary directory the state of the network interface for the node that is running
        the u'/fmoncentralpipecentral/mongoccentral/mongocentralcentral' task. We do this to check how much traffic does
        the central node receives with a centralised approach
        """
        netcheck_directory = ".netcheck"
        curl_node = list(self.masters)[0]
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout)
        mongo_tasks = filter(lambda task: task['appId'] == u'/fmoncentralpipecentral/mongoccentral/mongocentralcentral',
                             d.get('tasks'))
        mongo_host = mongo_tasks[0]['host']
        p = general_util.SshProcess('/sbin/ifconfig',
                                    host=mongo_host,
                                    shell=True,
                                    pty=True).run()
        now = strftime("%d_%b_%Y_%H:%M")
        if not exists(netcheck_directory):
            makedirs(netcheck_directory)
        with open('.netcheck/net_checkpoint' + now, 'w') as f:
            f.write(p.stdout)

    def check_elasticity(self, nslaves,force_pull,region):
        curl_node = list(self.masters)[0]
        general_util.replace_infile("fmone-resources/basic.json", "fmone-resources/exec.json", {"@nslaves@": nslaves,"@region@":region})
        general_util.Put(hosts=curl_node,
                         local_files=["fmone-resources/exec.json"],
                         remote_location="/home/vagrant/exec.json").run()
        p = general_util.SshProcess(
            'curl -X POST "http://leader.mesos/service/marathon-user/v2/apps" -H "content-type: application/json" -d@/home/vagrant/exec.json',
            host=curl_node).run()
        print p.stdout
        print p.stderr
        print "Sleeping for a while"
        sleep(60)
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout) # use the basic.json from fmone-resources
        fmone_tasks = filter(lambda task: task['appId'] == u'/fmone/fmones', d.get('tasks'))
        start_end = [(task.get('stagedAt'), task.get('startedAt')) for task in fmone_tasks]
        time_differences = map(lambda pair: mktime(strptime(pair[1][:-5], '%Y-%m-%dT%H:%M:%S')) -
                                            mktime(strptime(pair[0][:-5], '%Y-%m-%dT%H:%M:%S')), start_end)
        print "The mean time to start {0} nslaves instances with pulled {1} is: {2} and its variance {3}"\
                    .format(nslaves, force_pull, mean(time_differences), std(time_differences))
        p = general_util.SshProcess(
            'curl -X DELETE "http://leader.mesos/service/marathon-user/v2/groups/fmone" -H "content-type: application/json"',
            host=curl_node).run()
        sleep(20)
        return (nslaves, force_pull, mean(time_differences), std(time_differences))

    def check_resilience(self): # Would be possible to add the region here as a parameter?
        results = [] ## here we are going to include all of the results
        curl_node = list(self.masters)[0]
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout)
        fmone_tasks = filter(lambda task: task['appId'] == u'/fmonmongorpipe2/fmondocker2/fmoneagentdockerregion2', d.get('tasks'))
        kill_host = fmone_tasks[0].get('host')
        general_util.Remote('sudo docker rm -f $(sudo docker ps -a -q)',
                            hosts=kill_host,
                            process_args={"nolog_exit_code": True}).run()
        time1 = time()
        sleep(20) ## We leave some time till the fmone agent runs again
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                        host=curl_node).run()
        d = json.loads(p.stdout)
        killed_host = filter(lambda task: (task['host'] == kill_host),
                             d.get('tasks'))
        start_end = [(task.get('stagedAt'), task.get('startedAt')) for task in killed_host]
        time_differences = map(lambda pair: (mktime(strptime(pair[1][:-5], '%Y-%m-%dT%H:%M:%S'))) - (time1 - 7200) ,start_end)
        print "The mean time to recover for a Fmone agent is: {0} and its variance {1}"\
                    .format(mean(time_differences), std(time_differences))
        results.append(mean(time_differences))
        mongo_tasks = filter(lambda task: task['appId'] == u'/fmonmongorpipe2/mongor2/mongoregion2', d.get('tasks'))
        kill_host = mongo_tasks[0].get('host')
        general_util.Remote('sudo docker rm -f $(sudo docker ps -a -q)',
                            hosts=kill_host,
                            process_args={"nolog_exit_code": True}).run()
        time1 = time()
        sleep(60) ## we leave some time until all the fmone agents are up and running again
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout)
        fmone_tasks = filter(lambda task: task['appId'] == u'/fmonmongorpipe2/fmondocker2/fmoneagentdockerregion2', d.get('tasks'))
        df = pd.DataFrame(fmone_tasks)
        df['startedAt'] = pd.to_datetime(df['startedAt'])
        last_started = (df.sort_values('startedAt', ascending=False).head(1)['startedAt'].values[0].astype('uint64') / 1e9)
        print "The mean time to recover a Fmone pipeline is: {0}".format(last_started - time1)
        results.append(last_started - time1)
        general_util.Remote('sudo docker rm -f $(sudo docker ps -a -q)',
                            hosts=self.private_agents,
                            process_args={"nolog_exit_code": True}).run()
        time1 = time()
        sleep(260)
        p = general_util.SshProcess('curl "http://leader.mesos/service/marathon-user/v2/tasks"',
                                    host=curl_node).run()
        d = json.loads(p.stdout)
        fmone_tasks = filter(lambda task: task['appId'] == u'/fmonmongorpipe2/fmondocker2/fmoneagentdockerregion2', d.get('tasks'))
        df = pd.DataFrame(fmone_tasks)
        df['startedAt'] = pd.to_datetime(df['startedAt'])
        last_started = (df.sort_values('startedAt', ascending=False).head(1)['startedAt'].values[0].astype('uint64') / 1e9)
        print "The mean time to recover from a general failure is: {0}".format(last_started - time1)
        results.append(last_started - time1)
        return results


if __name__ == '__main__':
    home = "/Users/alvarobrandon/execo_experiments"
    experiments = ['/toma_buena_workloadf_Jun_2017_12:25',
                   '/toma_buena_workloade_23_Jun_2017',
                   '/toma_buena_workloadinsert_26_Jun_2017_12:05',
                   '/toma_buena_workload_update_26_Jun_2017_13:52',
                   '/toma_buena_workloada_y_b_21_Jun_2017_11:53',
                   '/toma_buena_workloadc_y_d_21_Jun_2017_15:58']
    directories = ["/with_fmone", "/no_fmone"]
    workloads = ["workloada", "workloadb", "workloadc", "workloadd", "workloade", "workloadf"]
    results = {}
    for exp in experiments:
        for d in directories:
            for w in workloads:
                list_of_metrics, metrics_mean, metrics_var = CassandraYCSB.analyse_results(directory=home + exp + d,
                                                                                           workload=w,
                                                                                           metric="Throughput")
                results[w + d] = (list_of_metrics, metrics_mean, metrics_var)
                print "For experiment {0} workload {1} and {2} the mean throughput is: {3} and variance {4}".format(exp,
                                                                                                                    w,
                                                                                                                    d,
                                                                                                                    metrics_mean,
                                                                                                                    metrics_var)
