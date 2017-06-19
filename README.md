## Conducere
---
Conducere, latin for conductor, defines an automate workflow of configuring large and ready to use OpenStack clusters from scratch by using open source tools and pre-defined templates. It has been developed by the EMS team of IAD group at National Institute of Standards and Technology (NIST), with our experience of evaluating data science projects which rely on large Hadoop, Spark clusters heavily.

The automate workflow has three steps:

1. Building a base image;
2. Creating an OpenStack cluster;
3. Configuring cluster nodes and bringing up services.

The first setup is optional. But a pre-baked base image that has many pre-installed software packages can be reused afterwards, therefore, will save a lot of time.

To implement the workflow, we use multiple tools including Packer, OpenStack Heat as well as Ansible, and has defined corresponding templates in three modules: image, heat_template and playbooks. These three module can work independently, for example, using only the playbooks module to configure an existing cluster. The followings are overviews of these modules, detailed explanations can be found in corresponding subdirectories.

#### Image module

[Packer](https://www.packer.io/) automates the creation of different types of virtual machine (VM) images for OpenStack, AWS EC2, Google Compute Engine, Virtual Box, etc.

We use Packer to build our base image. Packer builds an image by connecting to the target platform, spawning an instance and running the given provisioning scripts automatically. Once the provision is done, Packer stops the instance and create an image of it. We've defined a Packer file named `dse_vm.json` under image directory. It contains the information of target platform (OpenStack in this case), meta info of our target image and references to our configuring scripts.

#### Heat_tempolate module

[OpenStack Heat](https://wiki.openstack.org/wiki/Heat) provides a template based orchestration of OpenStack cluster. In a Heat template, we describe desired cluster spec, including:
* compute resources: number of nodes; for each node, its flavor (number of CPUs, memory size and disk size);
* network: router, network interfaces, network access rules;
* image for nodes (e.g. Ubuntu 14.04 cloud image or customized base image).

#### Playbook module

[Ansible](http://docs.ansible.com/ansible/index.html) is an automate system configuration tool. Ansible playbooks are Ansible's configuration, deployment, and orchestration language. They can describe a policy you want your remote systems to enforce. Ansible modules are building blocks that can be executed directly on remote hosts or through playbooks. Ansible ships with a number of modules managing systems' software packages, services, files, and etc.

We've created playbooks to provision clusters for data science projects. Currently, we support provision of

- Hadoop
- Spark
- Ganglia
- NFS
- NTP
- DMoni
- NIST_DSE_Wrapper
- Python 2.7, NumPy, SciPy, Scikit-learn, etc.

For complex and distributed frameworks or tools like Hadoop, Spark, Ganglia, NFS, NTP, DMoni, their playbooks are included in corresponding subdirectories.

Learned from best practices, we categorize cluster nodes into different roles: master, slave, client, and optionally storage. Each cluster can has one master (or multiple to avoid single point failure), many slaves/workers and many clients. A master node runs as a job scheduler or controller; Slaves nodes run jobs assigned to it by master; Users' applications reside in client nodes and talks the master node to get resources from cluster and execute their jobs. Currently, the playbooks work for Ubuntu 14.04. A few changes are needed for later Ubuntu version.

We also support to provision a single node cluster which itself acts as master, slave and client at the same time.

## Get started
---
We are going to provision a cluster consisting of a master, a client and three slave nodes. The cluster runs Hadoop, Spark, Ganglia, NFS and NTP. At the end, we will run a Hadoop application calculating Pi  on the cluster using quasi-Monte Carlo method.

### Prerequisites & installation

Assuming you already have access to an OpenStack project, the following tools are required:
* [Ansible](http://docs.ansible.com/ansible/intro_installation.html) (version >= 2.3)
* [Packer](https://www.packer.io/downloads.html) (version >= 1.0)
* [OpenStack command-line clients](https://docs.openstack.org/user-guide/common/cli-install-openstack-command-line-clients.html) (version >= 3.11)
* [Heat plugin for OpenStack command-line clients ](https://docs.openstack.org/user-guide/common/cli-install-openstack-command-line-clients.html) (version >= 1.9)

Ansible, OpenStack command-line clients and Heat plugin can be installed directly with Pip.

```bash
$ pip install ansible python-openstackclient python-heatclient
```

Once all the tools are installed, you need to setup your local environment to access OpenStack cluster.

1. Log into your Openstack Horizon interface;
2. From the Dashboard, go to *Project* -> *Access & Security* -> *API Access*;
3. Click *Download OpenStack RC File v2.0* to get the *PROJECT-openrc.sh* script that configures your environment variables;
4. Source *PROJECT-openrc.sh*
```
$ source PROJECT-openrc.sh
```

If you use *OpenStack RC File v3*, you may need to export following environment variables for Packer to talk to OpenStack using version 2 APIs.

```bash
$ export OS_TENANT_NAME=$OS_PROJECT_NAME
$ export OS_TENANT_ID=$OS_PROJECT_ID
$ export OS_DOMAIN_NAME='Your domain name'
```

You can test your environment by running an OpenStack command, for example, list all images.
```bash
$ openstack image list
```

### Provisioning a cluster

#### Step 1. Building a base image

Edit `image/base_image.json` Packer file. The file contains two parts: builders and provisioners.

```json
{
  "builders": [
    {
      "type": "openstack",
      "image_name": "Ubuntu 14.04_nist_base",
      "source_image": "bc5e15f8-49dc-484f-9aa0-4252f8867390",
      "ssh_username": "ubuntu",
      "flavor": "m1.small",
      "networks": ["912f026b-0061-4235-be9f-714eb269d58b"],
      "floating_ip": "192.168.0.2",
      "insecure": true
    }
  ],

  "provisioners": [
    {
      "type": "shell",
      "script": "install.sh"
    },
    {
      "type": "ansible-local",
      "playbook_file": "../playbooks/build_image.yml",
      "inventory_groups": ["base-image"],
      "playbook_dir": "../playbooks"
    }
  ]
}
```

The builders part describes target platform (OpenStack), the name of our base image (Ubuntu 14.04_nist_base), source image built upon (Ubuntu 14.04 with id  bc5e15f8-49dc-484f-9aa0-4252f8867390), and other info needed by Packer to spawn an instance in your OpenStack project. You need to customized some fields: id of `source_image`, id of `network`, `floating_ip`, etc. For more information about parameters, you can find at [Packer's OpenStack Builder](https://www.packer.io/docs/builders/openstack.html). It is useful and convenient to use OpenStack CLI to get ids of resources, such as `source_image` id and `network` id.

The provisioners part includes steps of configuring the instance. Firstly, it calls `image/install.sh` script to install Ansible. After that, it uses our Ansible playbooks to install software packages.

Validate your Packer file:
```bash
$ cd image
$ packer validate base_image.json
```

Build your base image:
```bash
$ packer build base_image.json
```
It's gonna take about 20-30min to download and install all the tools including Python, Pip, NumPy, SciPy, Ansible, JDK, Hadoop, Spark, Ganglia, etc.

#### Step 2. Creating a cluster


The cluster spec is defined in the Heat Orchestration Template file `heat-template/hot-template.yaml`.

Edit `heat-template/hot-template.yaml` to customize corresponding parameters for your cluster. The parameters are as follows.
 * The *image* to load on the nodes.
 * The *default-flavor* of the instances.
 * The number of slaves *slaves-count* and the number of clients *clients-count* (slaves and clients are only differentiated by their prefix)
 * The prefixes of the instances: *slaves-basename* and *clients-basename*
 * The *master-name*.
 * The *dns-nameservers* addresses to allow the nodes to access to the Internet, as a comma separated list.
 * A boolean parameter to set up the *floating ip address* on the master node. This functionality hasn't been tested yet. So far the best way to link a floating ip to the master node is to do it manually, or to uncomment the `fipass-0:` block line 150.
 * The *public_net* label of the public network for which floating IP addresses will be allocated.

Customize these parameters by editing the *default values* of the parameters.
```yaml
######## PARAMETERS SECTION STARTS HERE ########
# Parameters to customize the cluster
parameters:

# Default image used by the instances. The EMS system has been tested on Ubuntu 14.04 only so far.
  image:
    type: string
    label: image
    default: Ubuntu 14.04_DSE_base

    [...]


######## PARAMETERS SECTION END HERE ########
```

Create your cluster, namely stack in OpenStack:

```bash
$ openstack stack create -t hot-template.yaml mystack
```

Check stack status. Once the stack is created, the status becomes *CREATE_COMPLETED* from *CREATE_IN_PROGRESS*.

```bash
$ openstack stack show mystack -f json
```

Get the SSH credentials to connect to your nodes.

* Log into your OpenStack project Dashboard, and go to *Orchestration* -> *Stacks* ->*Your Stack* -> *Overview*.
* From this panel, copy the private key value listed as *private_ssh_key*.
* Save it into a file.
* SSH requires the private key files to have *special access authorizations*. Set it using the following:

```shell
chmod 600 /path/to/your/private-key-file
```

Add this identity to your ssh-agent:

```shell
ssh-add /path/to/your/private-key-file
```

Connect to your node through ssh:
The node has to be associated with a floating ip address. Also, the _ubuntu_ user name may be different if the image used is not an Ubuntu distribution.
```shell
ssh -A ubuntu@floating-ip-address
```

You can delete your stack using following command:
```bash
$ openstack stack delete mystack
```

To get further information about how to bring up a cluster using Heat, check the heat-template/README.md guide.

#### Step 3. Configuring the cluster

You can configure the cluster either on your localhost or on the master node of your cluster. We recommend to ssh into the master node and configure your cluster there, since Ansible needs to reach all your cluster nodes. By doing this, we only need to allocate one floating IP for the master node.

If you choose to configure on your master node, copy playbooks to it and SSH to it with forwarding your ssh key:

```bash
$ scp -r ./playbooks ubuntu@master:~
$ ssh -A ubuntu@master
```

Edit `/etc/hosts` file and add all the cluster nodes's hostname and IP address, since Ansible uses hostnames to connect to the nodes. For example,

```
...

10.10.0.4 master
10.10.0.6 slave-0
10.10.0.5 slave-1
10.10.0.8 slave-2
10.10.0.7 client-0
```

Edit Ansible inventory file `cluster` and add cluster nodes to corresponding categories:

```yaml
[dse_master]
master ipv4=10.10.0.4

[dse_slaves]
slave-0 ipv4=10.10.0.6
slave-1 ipv4=10.10.0.5
slave-2 ipv4=10.10.0.8

[dse_client]
client-0 ipv4=10.10.0.7

...
```

Configure slave nodes:

```bash
$ ansible-playbook -i cluster --tags common,ntp,hadoop-config,ganglia,nfs slave.yml
```

Configure master node:
```bash
$ ansible-playbook -i cluster --tags common,ntp,hadoop-config,hadoop-start,spark-config,ganglia,nfs master.yml
```

Configure client node:

```bash
$ ansible-playbook -i cluster --tags common,ntp,hadoop-config,spark-config,ganglia client.yml
```

Ansible uses *tags* to select tasks to execute. For more information to have finer control over tasks, please see playbooks module.

#### Step 4. Testing

Run a Hadoop application calculating Pi on the cluster. For convenience, we have created a task for this testing.

```bash
$ ansible-playbook -i cluster --tags hadoop-test client.yml
```

It will start the application on the client node, which talks to master to schedule its jobs to execute on slaves.

### How to use the cluster

## Contact

## License
