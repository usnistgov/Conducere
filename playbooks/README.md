## Overview

DSE-ansible automatically configures a cluster for data science projects
with tools installed and running by employing Ansible.

Currently, it suppports several frameworks or tools consisting of
- Hadoop
- Spark
- Ganglia
- DMoni
- NIST_DSE_Wrapper
- NTP
- Python 2.7, NumPy, SciPy, Scikit-learn, etc.

Each of them has a sub-directory, namely Ansible module, including Ansible playbooks
and variables which defines how to install, configure, run, stop and test
corresponding tool.

A cluster can be configured in two modes: 
- standalone mode, and 
- cluster mode

In standalone mode, there is only one node which has everything installed and running;
In cluster mode, there are three possible roles for a node, namely master, slave
and client, corresponding to master.yml, slave.yml and client.yml respectively.
In the current configuration, master role runs all the master services of Hadoop,
Ganglia, DMoni and NTP; slave role runs worker or slave services; a node acting 
as a client will have user's application installed and talks to master only to
execute Haddop or Spark jobs. All basic tools, such as Python, are install for
all roles.

DSE-ansible is tested on Ubuntu 14.04. Small changes might be needed for newer
Ubuntu versions.


## Installation 

- Install [Ansible](http://docs.ansible.com/ansible/intro_installation.html);
- Clone this repo;
- Download Hadoop, Spark and DMoni packages and put them in bundles folder.
  * [hadoop-2.7.2](http://www.apache.org/dyn/closer.cgi/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz)
  * [spark-2.0.2-bin-hadoop2.7](http://spark.apache.org/downloads.html)
  * [dmoni-0.9.0](https://github.com/usnistgov/dmoni/files/1045176/dmoni-0.9.0.tar.gz)

## Get Started

### Provisioning a standalone node

Assuming 1) a new Ubuntu14.04 VM is running; 3) the hostname of the VM is 
dse-standalone.2) it is reachable through ssh with the hostname (e.g. ssh
ubuntu@dse-standalone). You might need to add the hostname and corresponding
ip address to your localhost's /etc/hosts file. Note: Haddop does not accept
hostname with underscore, e.g. dse_standalone will not work. It is recommended
for the target node to have more that 4 cpu and 8GB of memory for running or
testing Hadoop.

#### Step 1. Specifying target host and variables

The target host info are specified in an Ansible inventory file, namely standalone.

```yml
[standalone]
dse-standalone ipv4=10.0.0.72

[standalone:vars]
hadoop_namenode='dse-standalone'
hadoop_resource_manager='dse-standalone'
hadoop_slaves=['dse-standalone']
hadoop_users=['hduser', 'ubuntu']
```

The standalone file consists of two sections. The first section [standalone] 
defines the target host's `hostname` (dse-standalone) and `ipv4` address (10.0.0.72).
The second section [standalone:vars] defines variables that will be used by hadoop
playbooks. In this example, the `hadoop_namenode`, `hadoop_resource_manager` and
`hadoop_slaves` are the same; two haddop users, `hduser` and `ubuntu`, should be created.

> Ubuntu 16.04: run `apt-get install libssl-dev` and edit `hadoop/vars.yml` to use jre-8 instead of jre-7.

#### Step 2. Provisioning target host

The playbook for provisioning a standalone node is standalone.yml. It includes
a list of tasks with tags. The defined tags help filter the tasks executed. 
Followings are a part of the task list.

```yml
  tasks:

  - name: Install common tools
    include: common.yml
    tags: ['install']
    
  - name: Install hadoop
    include: hadoop/install.yml
    tags: ['install', 'hadoop-install']

  - name: Configure hadoop standalone
    include: hadoop/config_standalone.yml
    tags: ['install', 'hadoop-config']

  - name: Run hadoop
    include: hadoop/run.yml
    become_user: hduser
    become: true
    tags: ['hadoop-start']

```

We can see each task has a name as well as a list of tags, and includes another
playbook file which defines sub-tasks. For example, the ```Install hadoop``` task
tagged with ```install``` and ```hadoop-install```, has sub-tasks defined in 
```hadoop/install.yml``` file.

In this step, we will install all the tools by executing the playbook with 
```intall``` tag:

```bash
$ ansible-playbook -i standalone --tags install standalone.yml

...
```

It will take some time (>10 minutes), since many tools require download and
installation, such as python-dev, python-pip, git, etc.

Next, we want to start Hadoop services on the node, which can be done by 
running the playbook with ```hadoop-start``` tag.

```bash
$ ansible-playbook -i standalone --tags hadoop-start standalone.yml 
```

If you want to stop Hadoop services, you can run with ```hadoop-stop``` tag.

```bash
$ ansible-playbook -i standalone --tags hadoop-stop standalone.yml 
```

You can have more control over tasks to be executed by choosing tags.

#### Step 3. Testing

List Hadoop processes. The following command will start a shell and run ``jps``
command on the node and print out its stdout and stderr. Similarly, you can run
other commands on the target node.

```bash
$ ansible -i standalone dse-standalone -m shell  -a "sudo jps -l"
dse-standalone | SUCCESS | rc=0 >>
24629 org.apache.hadoop.yarn.server.nodemanager.NodeManager
19063 org.apache.hadoop.hdfs.server.datanode.DataNode
25226 org.apache.hadoop.mapreduce.v2.hs.JobHistoryServer
26168 sun.tools.jps.Jps
24485 org.apache.hadoop.yarn.server.resourcemanager.ResourceManager
19297 org.apache.hadoop.hdfs.server.namenode.SecondaryNameNode
18918 org.apache.hadoop.hdfs.server.namenode.NameNode
```

Run a Pi calculation job on Hadoop. The task is defined in hadoop/test.yml.

```bash
$ ansible-playbook -i standalone --tags hadoop-test standalone.yml
...
TASK [Test if Hadoop is functioning by running a Pi calculation.] **************
changed: [dse-standalone]

TASK [debug] *******************************************************************
ok: [dse-standalone] => {
    "msg": {
        "changed": true, 
        "cmd": [
            "yarn", 
            "jar", 
            "/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar", 
            "pi", 
            "2", 
            "1000"
        ], 
        "delta": "0:00:28.978728", 
        "end": "2017-03-20 15:43:17.791692", 
        "rc": 0, 
        "start": "2017-03-20 15:42:48.812964", 
        "stderr": "17/03/20 15:42:52 INFO client.RMProxy: Connecting to ResourceManager at dse-standalone/10.0.0.97:8032\n17/03/20 15:42:52 INFO input.FileInputFormat: Total input paths to process : 2\n17/03/20 15:42:53 INFO mapreduce.JobSubmitter: number of splits:2\n17/03/20 15:42:53 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1490024445794_0001\n17/03/20 15:42:53 INFO impl.YarnClientImpl: Submitted application application_1490024445794_0001\n17/03/20 15:42:53 INFO mapreduce.Job: The url to track the job: http://dse-standalone:8088/proxy/application_1490024445794_0001/\n17/03/20 15:42:53 INFO mapreduce.Job: Running job: job_1490024445794_0001\n17/03/20 15:43:03 INFO mapreduce.Job: Job job_1490024445794_0001 running in uber mode : false\n17/03/20 15:43:03 INFO mapreduce.Job:  map 0% reduce 0%\n17/03/20 15:43:09 INFO mapreduce.Job:  map 100% reduce 0%\n17/03/20 15:43:16 INFO mapreduce.Job:  map 100% reduce 100%\n17/03/20 15:43:17 INFO mapreduce.Job: Job job_1490024445794_0001 completed successfully\n17/03/20 15:43:17 INFO mapreduce.Job: Counters: 49\n\tFile System Counters\n\t\tFILE: Number of bytes read=50\n\t\tFILE: Number of bytes written=353574\n\t\tFILE: Number of read operations=0\n\t\tFILE: Number of large read operations=0\n\t\tFILE: Number of write operations=0\n\t\tHDFS: Number of bytes read=530\n\t\tHDFS: Number of bytes written=215\n\t\tHDFS: Number of read operations=11\n\t\tHDFS: Number of large read operations=0\n\t\tHDFS: Number of write operations=3\n\tJob Counters \n\t\tLaunched map tasks=2\n\t\tLaunched reduce tasks=1\n\t\tData-local map tasks=2\n\t\tTotal time spent by all maps in occupied slots (ms)=8206\n\t\tTotal time spent by all reduces in occupied slots (ms)=3670\n\t\tTotal time spent by all map tasks (ms)=8206\n\t\tTotal time spent by all reduce tasks (ms)=3670\n\t\tTotal vcore-milliseconds taken by all map tasks=8206\n\t\tTotal vcore-milliseconds taken by all reduce tasks=3670\n\t\tTotal megabyte-milliseconds taken by all map tasks=8402944\n\t\tTotal megabyte-milliseconds taken by all reduce tasks=3758080\n\tMap-Reduce Framework\n\t\tMap input records=2\n\t\tMap output records=4\n\t\tMap output bytes=36\n\t\tMap output materialized bytes=56\n\t\tInput split bytes=294\n\t\tCombine input records=0\n\t\tCombine output records=0\n\t\tReduce input groups=2\n\t\tReduce shuffle bytes=56\n\t\tReduce input records=4\n\t\tReduce output records=0\n\t\tSpilled Records=8\n\t\tShuffled Maps =2\n\t\tFailed Shuffles=0\n\t\tMerged Map outputs=2\n\t\tGC time elapsed (ms)=157\n\t\tCPU time spent (ms)=2670\n\t\tPhysical memory (bytes) snapshot=722366464\n\t\tVirtual memory (bytes) snapshot=2503884800\n\t\tTotal committed heap usage (bytes)=560988160\n\tShuffle Errors\n\t\tBAD_ID=0\n\t\tCONNECTION=0\n\t\tIO_ERROR=0\n\t\tWRONG_LENGTH=0\n\t\tWRONG_MAP=0\n\t\tWRONG_REDUCE=0\n\tFile Input Format Counters \n\t\tBytes Read=236\n\tFile Output Format Counters \n\t\tBytes Written=97", 
        "stdout": "Number of Maps  = 2\nSamples per Map = 1000\nWrote input for Map #0\nWrote input for Map #1\nStarting Job\nJob Finished in 25.212 seconds\nEstimated value of Pi is 3.14400000000000000000", 
        "stdout_lines": [
            "Number of Maps  = 2", 
            "Samples per Map = 1000", 
            "Wrote input for Map #0", 
            "Wrote input for Map #1", 
            "Starting Job", 
            "Job Finished in 25.212 seconds", 
            "Estimated value of Pi is 3.14400000000000000000"
        ], 
        "warnings": []
    }
}
```

### Provisioning a cluster

In this exmaple, we will provision a cluster with a master, three slaves and
a client node. We assume that all nodes are 1) up and running Ubuntu14.04, and
2) reachable through ssh with their hostnames (e.g. ssh
ubuntu@dse-node-0). You might need to add the hostname and corresponding
ip address to /etc/hosts file.

#### Step 1. Specifying cluster nodes and variables

The inventory file named `cluster` defines nodes and variables (see below). The `dse_master`,
`dse_slaves` and `dse_client` sections group nodes into three categories (master,
slave and client). The `dse_cluster` section groups
all nodes together to form a cluster. These group names are used to reference 
corresponding nodes later on. Cluster-wide variables are defined in 
`[dse_cluster:vars]` section; Client variables are defined in `[dse_client:vars]`
section.

```yml
[dse_master]
dse-node-1 ipv4=10.0.0.98

[dse_slaves]
dse-node-2 ipv4=10.0.0.99
dse-node-3 ipv4=10.0.0.102
dse-node-4 ipv4=10.0.0.101

[dse_client]
dse-node-5 ipv4=10.0.0.100

[dse_cluster:children]
dse_master
dse_slaves
dse_client

[dse_cluster:vars]
hadoop_namenode="{{ groups.dse_master[0] }}"
hadoop_resource_manager="{{ groups.dse_master[0] }}"
hadoop_slaves="{{ groups.dse_slaves }}"
hadoop_users=['hduser', 'ubuntu', 'root']
dmoni_manager="{{ groups.dse_master[0] }}"
dmoni_storage="http://192.168.0.3:9200"
ganglia_master="{{ groups.dse_master[0] }}"
ntp_local_server="{{ groups.dse_master[0] }}"

[dse_client:vars]
hadoop_users=['hduser', 'ubuntu']
```
#### Step 2. Provisioning slave nodes

We will install tools on slave nodes and start all services except Hadoop
services since they are launched by Hadoop master. The services to be started include
Ganglia's ganglia-monitor, DMoni's agent, and NTP server syncing with master.

```bash
$ ansible-playbook -i cluster --tags pre-install,ntp,hadoop,spark,ganglia,dmoni slave.yml

PLAY [dse_slaves] **************************************************************

TASK [setup] *******************************************************************
The authenticity of host 'dse-node-2 (10.0.0.99)' can't be established.
ECDSA key fingerprint is 51:35:40:36:ee:b0:72:2d:1a:52:b9:81:20:46:e4:36.
Are you sure you want to continue connecting (yes/no)? The authenticity of host 'dse-node-3 (10.0.0.102)' can't be established.
ECDSA key fingerprint is db:7a:01:47:e0:f2:75:0f:f1:07:e5:6d:6d:e2:8d:34.
Are you sure you want to continue connecting (yes/no)? The authenticity of host 'dse-node-4 (10.0.0.101)' can't be established.
ECDSA key fingerprint is 1b:65:e5:16:e3:b0:ba:c7:d1:61:23:39:44:a9:73:d7.
Are you sure you want to continue connecting (yes/no)? yes
yes
yes
ok: [dse-node-2]
ok: [dse-node-3]
ok: [dse-node-4]

TASK [Update apt cache] ********************************************************
changed: [dse-node-4]
changed: [dse-node-3]
changed: [dse-node-2]

TASK [Install common tools] ****************************************************
ok: [dse-node-2] => (item=[u'git', u'zsh', u'vim', u'python-dev', u'python-pip', u'python-numpy', u'python-scipy'])
ok: [dse-node-3] => (item=[u'git', u'zsh', u'vim', u'python-dev', u'python-pip', u'python-numpy', u'python-scipy'])
ok: [dse-node-4] => (item=[u'git', u'zsh', u'vim', u'python-dev', u'python-pip', u'python-numpy', u'python-scipy'])
...
```

We can see each task is executed on three slave nodes.

#### Step 3. Provisioning master node

In this step, we install tools and start services on master node.The master node
runs Hadoop master services (YARN
ResourceManager, HDFS NameNode, JobHistory server), Ganglia's gmetad and 
ganglia-monitor, DMoni's manger and agent, and NTP server synced with outside source.
The Hadoop master services will talk to slave nodes and start slave services
(NodeManager and DataNode processes) on them.

Firstly, we need to add `hduser`'s private key to local ssh-agent, since some tasks
are executed by `hduser` user and Ansible needs to ssh to the node as `hduser`. 
The key is in `bundle/ssh_keys/hduser/` directory.

```bash
$ ssh-add ./bundle/ssh_keys/hduser/id_rsa                                                                                    merge_with_master_after_readme!?
Identity added: ./bundle/ssh_keys/hduser/id_rsa (./bundle/ssh_keys/hduser/id_rsa)
```

Provisioning master node:

```bash
$ ansible-playbook -i cluster --tags pre-install,ntp,hadoop,spark,ganglia,dmoni master.yml
...
TASK [Start DMoni manager daemon] **********************************************
changed: [dse-node-1]

TASK [debug] *******************************************************************
ok: [dse-node-1] => {
    "msg": {
        "changed": true,
        "cmd": "dmoni_manager.sh start",
        "delta": "0:00:01.010192",
        "end": "2017-04-28 15:59:02.581935",
        "rc": 0,
        "start": "2017-04-28 15:59:01.571743",
        "stderr": "",
        "stdout": "starting DMoni manager\n2017/04/28 15:59:01 Dmoni Manager (ID: 94712721-1600-4b60-84bb-03006a81f3b7, Address: dse-node-1:5300)",
        "stdout_lines": [
            "starting DMoni manager",
            "2017/04/28 15:59:01 Dmoni Manager (ID: 94712721-1600-4b60-84bb-03006a81f3b7, Address: dse-node-1:5300)"
        ],
        "warnings": []
    }
}

TASK [include_vars] ************************************************************
ok: [dse-node-1]

TASK [Start DMoni agent daemon] ************************************************
changed: [dse-node-1]

TASK [debug] *******************************************************************
ok: [dse-node-1] => {
    "msg": {
        "changed": true,
        "cmd": "dmoni_agent.sh start",
        "delta": "0:00:01.008916",
        "end": "2017-04-28 15:59:05.941109",
        "rc": 0,
        "start": "2017-04-28 15:59:04.932193",
        "stderr": "",
        "stdout": "starting DMoni agent\n2017/04/28 15:59:04 Dmoni Agent (ID: 01d65520-c872-4449-92a0-b7c11442f604, Address: dse-node-1:5301)",
        "stdout_lines": [
            "starting DMoni agent",
            "2017/04/28 15:59:04 Dmoni Agent (ID: 01d65520-c872-4449-92a0-b7c11442f604, Address: dse-node-1:5301)"
        ],
        "warnings": []
    }
}

PLAY RECAP *********************************************************************
dse-node-1                 : ok=77   changed=45   unreachable=0    failed=0
```

#### Step 4. Provisioning client node

We will install and configure tools, as well as start some services on client node.
The services include ganglia-monitor, DMoni's agent, NTP server synced with master.
Hadoop is installed but does not run any service, since it only serves as a client
and it's user's applicaitons that call it to talk to master to execute jobs.

```bash
$ ansible-playbook -i cluster --tags pre-install,ntp,hadoop,spark,ganglia,dmoni client.yml
PLAY [dse_client] **************************************************************

TASK [setup] *******************************************************************
The authenticity of host 'dse-node-5 (10.0.0.103)' can't be established.
ECDSA key fingerprint is 73:18:19:0a:01:ec:5b:72:93:3b:a8:bc:65:d6:50:f8.
Are you sure you want to continue connecting (yes/no)? yes
ok: [dse-node-5]

TASK [Update apt cache] ********************************************************
changed: [dse-node-5]

TASK [Install common tools] ****************************************************
ok: [dse-node-5] => (item=[u'git', u'zsh', u'vim', u'python-dev', u'python-pip', u'python-numpy', u'python-scipy'])

TASK [Ensure cluster hosts are in /etc/hosts] **********************************
changed: [dse-node-5]

TASK [Install ntp] *************************************************************
changed: [dse-node-5]

TASK [Ensure ntp's configuration files exist] **********************************
changed: [dse-node-5] => (item=ntp.conf.j2)

TASK [Restart ntp server] ******************************************************
changed: [dse-node-5]

TASK [include_vars] ************************************************************
ok: [dse-node-5]

...
```

#### Step 5. Testing

##### Checking if Hadoop services are running.

Run `jps` command on each node, which will list all Hadoop processes running.

```bash
$ ansible -i cluster dse_cluster -m shell  -a "sudo jps"
dse-node-5 | SUCCESS | rc=0 >>
22579 Jps

dse-node-2 | SUCCESS | rc=0 >>
21129 Jps
18464 NodeManager
18294 DataNode

dse-node-1 | SUCCESS | rc=0 >>
22865 ResourceManager
17534 SecondaryNameNode
23377 JobHistoryServer
8974 Jps
17300 NameNode

dse-node-4 | SUCCESS | rc=0 >>
18460 NodeManager
21138 Jps
18290 DataNode

dse-node-3 | SUCCESS | rc=0 >>
21128 Jps
18461 NodeManager
18291 DataNode
```

We can see that master node `dse-node-1` has ResourceManager, NameNode, 
SecondaryNameNode and JobHistoryServer processes running. On the other hand, 
the slave nodes (dse-node-2, dse-node-3 and dse-node-4) have NodeManager and 
DataNode services running.

##### Checking DMoni's manager and agents

Run `ps aux | grep dmoni` commands on each node to see if there are DMoni 
Manager process on master node and Agent processes on slave and client nodes.

```bash
ansible -i cluster dse_cluster -m shell  -a "ps aux | grep dmoni"                                                        1 merge_with_master_after_readme!?
dse-node-5 | SUCCESS | rc=0 >>
root     21217  0.0  0.2 268740  8816 ?        Sl   18:07   0:00 dmoni agent --storage http://192.168.0.3:9200 --manager dse-node-1 --manager-port 5300 --host dse-node-5 --port 5301
ubuntu   22903  0.0  0.0   4440   636 pts/0    S+   18:30   0:00 /bin/sh -c ps aux | grep dmoni
ubuntu   22905  0.0  0.0  10460   912 pts/0    S+   18:30   0:00 grep dmoni

dse-node-1 | SUCCESS | rc=0 >>
root      5169  0.0  0.2 130660  9068 ?        Sl   15:59   0:01 dmoni manager --storage http://192.168.0.3:9200 --host dse-node-1 --app-port 5500 --node-port 5300
root      5418  0.0  0.2 286320 10136 ?        Sl   15:59   0:02 dmoni agent --storage http://192.168.0.3:9200 --manager dse-node-1 --manager-port 5300 --host dse-node-1 --port 5301
ubuntu    9323  0.0  0.0   4440   636 pts/0    S+   18:30   0:00 /bin/sh -c ps aux | grep dmoni
ubuntu    9325  0.0  0.0  10464   912 pts/0    S+   18:30   0:00 grep dmoni

dse-node-4 | SUCCESS | rc=0 >>
root     17689  0.0  0.2 138856 10388 ?        Sl   14:59   0:04 dmoni agent --storage http://192.168.0.3:9200 --manager dse-node-1 --manager-port 5300 --host dse-node-4 --port 5301
ubuntu   21464  0.0  0.0   4440   640 pts/0    S+   18:30   0:00 /bin/sh -c ps aux | grep dmoni
ubuntu   21466  0.0  0.0  10464   912 pts/0    S+   18:30   0:00 grep dmoni

dse-node-2 | SUCCESS | rc=0 >>
root     17688  0.0  0.2 204392 10380 ?        Sl   14:59   0:04 dmoni agent --storage http://192.168.0.3:9200 --manager dse-node-1 --manager-port 5300 --host dse-node-2 --port 5301
ubuntu   21456  0.0  0.0   4440   640 pts/0    S+   18:30   0:00 /bin/sh -c ps aux | grep dmoni
ubuntu   21458  0.0  0.0  10464   916 pts/0    S+   18:30   0:00 grep dmoni

dse-node-3 | SUCCESS | rc=0 >>
root     17686  0.0  0.2 269928  8352 ?        Sl   14:59   0:04 dmoni agent --storage http://192.168.0.3:9200 --manager dse-node-1 --manager-port 5300 --host dse-node-3 --port 5301
ubuntu   21454  0.0  0.0   4440   636 pts/0    S+   18:30   0:00 /bin/sh -c ps aux | grep dmoni
ubuntu   21456  0.0  0.0  10464   916 pts/0    S+   18:30   0:00 grep dmoni
```

##### Calculating Pi using Hadoop cluster

We want to launch a Pi calculation application on client node, which will submit
a job to Hadoop master. The master then runs the computation on slave nodes and returns
results to client at the end.

```bash
ansible-playbook -i cluster --tags hadoop-test client.yml

PLAY [dse_client] **************************************************************

TASK [setup] *******************************************************************
ok: [dse-node-5]

TASK [include_vars] ************************************************************
ok: [dse-node-5]

TASK [Test if Hadoop is functioning by running a Pi calculation.] **************
changed: [dse-node-5]

TASK [debug] *******************************************************************
ok: [dse-node-5] => {
    "msg": {
        "changed": true,
        "cmd": [
            "yarn",
            "jar",
            "/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar",
            "pi",
            "2",
            "1000"
        ],
        "delta": "0:00:37.821840",
        "end": "2017-04-28 18:34:25.670022",
        "rc": 0,
        "start": "2017-04-28 18:33:47.848182",
        "stderr": "17/04/28 18:33:52 INFO client.RMProxy: Connecting to ResourceManager at dse-node-1/10.0.0.98:8032\n17/04/28 18:33:53 INFO input.FileInputFormat: Total input paths to process : 2\n17/04/28 18:33:54 INFO mapreduce.JobSubmitter: number of splits:2\n17/04/28 18:33:54 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1493394947841_0001\n17/04/28 18:33:55 INFO impl.YarnClientImpl: Submitted application application_1493394947841_0001\n17/04/28 18:33:55 INFO mapreduce.Job: The url to track the job: http://dse-node-1:8088/proxy/application_1493394947841_0001/\n17/04/28 18:33:55 INFO mapreduce.Job: Running job: job_1493394947841_0001\n17/04/28 18:34:23 INFO mapred.ClientServiceDelegate: Application state is completed. FinalApplicationStatus=SUCCEEDED. Redirecting to job history server\n17/04/28 18:34:24 INFO mapreduce.Job: Job job_1493394947841_0001 running in uber mode : false\n17/04/28 18:34:24 INFO mapreduce.Job:  map 100% reduce 100%\n17/04/28 18:34:25 INFO mapreduce.Job: Job job_1493394947841_0001 completed successfully\n17/04/28 18:34:25 INFO mapreduce.Job: Counters: 50\n\tFile System Counters\n\t\tFILE: Number of bytes read=50\n\t\tFILE: Number of bytes written=353487\n\t\tFILE: Number of read operations=0\n\t\tFILE: Number of large read operations=0\n\t\tFILE: Number of write operations=0\n\t\tHDFS: Number of bytes read=524\n\t\tHDFS: Number of bytes written=215\n\t\tHDFS: Number of read operations=11\n\t\tHDFS: Number of large read operations=0\n\t\tHDFS: Number of write operations=3\n\tJob Counters \n\t\tLaunched map tasks=2\n\t\tLaunched reduce tasks=1\n\t\tData-local map tasks=1\n\t\tRack-local map tasks=1\n\t\tTotal time spent by all maps in occupied slots (ms)=15614\n\t\tTotal time spent by all reduces in occupied slots (ms)=5627\n\t\tTotal time spent by all map tasks (ms)=15614\n\t\tTotal time spent by all reduce tasks (ms)=5627\n\t\tTotal vcore-milliseconds taken by all map tasks=15614\n\t\tTotal vcore-milliseconds taken by all reduce tasks=5627\n\t\tTotal megabyte-milliseconds taken by all map tasks=15988736\n\t\tTotal megabyte-milliseconds taken by all reduce tasks=5762048\n\tMap-Reduce Framework\n\t\tMap input records=2\n\t\tMap output records=4\n\t\tMap output bytes=36\n\t\tMap output materialized bytes=56\n\t\tInput split bytes=288\n\t\tCombine input records=0\n\t\tCombine output records=0\n\t\tReduce input groups=2\n\t\tReduce shuffle bytes=56\n\t\tReduce input records=4\n\t\tReduce output records=0\n\t\tSpilled Records=8\n\t\tShuffled Maps =2\n\t\tFailed Shuffles=0\n\t\tMerged Map outputs=2\n\t\tGC time elapsed (ms)=246\n\t\tCPU time spent (ms)=2560\n\t\tPhysical memory (bytes) snapshot=692834304\n\t\tVirtual memory (bytes) snapshot=2472390656\n\t\tTotal committed heap usage (bytes)=521142272\n\tShuffle Errors\n\t\tBAD_ID=0\n\t\tCONNECTION=0\n\t\tIO_ERROR=0\n\t\tWRONG_LENGTH=0\n\t\tWRONG_MAP=0\n\t\tWRONG_REDUCE=0\n\tFile Input Format Counters \n\t\tBytes Read=236\n\tFile Output Format Counters \n\t\tBytes Written=97",
        "stdout": "Number of Maps  = 2\nSamples per Map = 1000\nWrote input for Map #0\nWrote input for Map #1\nStarting Job\nJob Finished in 32.628 seconds\nEstimated value of Pi is 3.14400000000000000000",
        "stdout_lines": [
            "Number of Maps  = 2",
            "Samples per Map = 1000",
            "Wrote input for Map #0",
            "Wrote input for Map #1",
            "Starting Job",
            "Job Finished in 32.628 seconds",
            "Estimated value of Pi is 3.14400000000000000000"
        ],
        "warnings": []
    }
}
```
