## Conducere

Conducere, latin for conductor, defines an automated workflow for configuring large, ready-to-use OpenStack clusters using open-source tools and predefined templates. It has been developed by the Evaluation Management System team of the Information Access Division at the National Institute of Standards and Technology (NIST) based on our experience evaluating data science projects that rely heavily on large Hadoop and Spark clusters.

The Conducere workflow has three steps:

1. Build a base image
2. Create an OpenStack cluster
3. Configure cluster nodes and bring up services

Note: The first step is optional, but a pre-baked base image with many pre-installed software packages that can be reused afterwards will save time later on.

To implement the workflow, we used multiple tools including Packer, OpenStack Heat, and Ansible. To do so, we have defined corresponding templates for each of these three tools which are available in the three modules provided in this repository: Image, Heat_template, and Playbooks. While we have written these modules to work together for this project, they can also be used independently if nessesary. For example, one could use only the Playbooks module to configure an existing cluster. Breif overviews of these three modules can be found below with more detailed descriptions available in their respective subdirectories.

#### Image Module

[Packer](https://www.packer.io/) is an open-source tool used to automate the creation of different types of virtual machine (VM) images for OpenStack, AWS EC2, Google Compute Engine, Oracle VirtualBox, etc. We used Packer to build our base image. It builds an image by connecting to the target platform, spawning an instance, and running the given provisioning scripts automatically. Once the provisioning is done, Packer stops the instance and saves an image of it. We've defined a Packer file named `dse_vm.json` under the image subdirectory of this repository. It contains information about the target platform (OpenStack in this case), meta information of our target image, and references to our configuration scripts.

#### Heat_template Module

[OpenStack Heat](https://wiki.openstack.org/wiki/Heat) provides a template based orchestration of an OpenStack cluster. In our Heat template, we describe our desired cluster spec, including:
* compute resources: number of nodes and, for each node, its flavor (number of CPUs, memory size and disk size)
* network configuration: router, network interfaces, and network access rules
* node configuration: desired image for the nodes (e.g. Ubuntu 14.04 cloud image or customized base image).

#### Playbook Module

[Ansible](http://docs.ansible.com/ansible/index.html) is an automated system configuration tool. Ansible does so using Playbooks, which is Ansible's configuration, deployment, and orchestration language. Playbooks instruct Ansible's modules on how to configure the remote machines. Ansible modules are the building blocks that can be executed directly on remote hosts or through Playbooks. Ansible ships with a number of modules managing systems' software packages, services, files, and etc.

We've created a custom Playbooks configuration to provision clusters specifically for data science projects. Currently, we support provisioning of

- Hadoop
- Spark
- Ganglia
- NFS
- NTP
- DMoni
- NIST_DSE_Wrapper
- Python 2.7, NumPy, SciPy, Scikit-learn, etc.

For complex, distributed frameworks and tools, such as Hadoop, Spark, Ganglia, NFS, NTP, and DMoni, Playbooks are included in corresponding subdirectories.

Learning from best practices, we categorize cluster nodes into different roles: master, slave, client, and, optionally, storage. Each cluster can have one master (or multiple to avoid having a single point of failure), many slaves/workers, and many clients. A master node functions as a job scheduler or controller for the cluster. Slave nodes are workers that run jobs assigned to them by the master. Client nodes handle user applications and talk to the master node to procure nessesary cluster resources and schedule jobs. The cluster need not follow this format. For example, we also support provisioning a single node cluster which simultaneously acs as a master, slave, and client. Currently, our Playbooks have been tested on Ubuntu 14.04. A few changes may be needed for compatibility with later Ubuntu versions.

## Getting Started

In this tutorial, we are going to provision a cluster consisting of one master, one client, and three slave nodes. The cluster runs Hadoop, Spark, Ganglia, NFS and NTP. At the end, we will run a Hadoop application calculating Pi on the cluster using quasi-Monte Carlo method.

### Prerequisites & installation

We assume you already have access to an OpenStack project as well as experience using OpenStack. Additionally, the following tools are required:
* [Ansible](http://docs.ansible.com/ansible/intro_installation.html) (version >= 2.3)
* [Packer](https://www.packer.io/downloads.html) (version >= 1.0)
* [OpenStack command-line clients](https://docs.openstack.org/user-guide/common/cli-install-openstack-command-line-clients.html) (version >= 3.11)
* [Heat plugin for OpenStack command-line clients ](https://docs.openstack.org/user-guide/common/cli-install-openstack-command-line-clients.html) (version >= 1.9)

Packer can be installed by following the instructions provided [here](https://www.packer.io/intro/getting-started/install.html).

Ansible, OpenStack command-line clients, and Heat plugin can be installed using the following pip command.

```bash
$ pip install ansible python-openstackclient python-heatclient
```

Once all the tools are installed, you need to setup your local environment to access OpenStack project.

1. Log into your Openstack Horizon interface
2. From the Dashboard, go to *Project* -> *Access & Security* -> *API Access*
3. Click *Download OpenStack RC File v2.0* to get the *PROJECT-openrc.sh* script that configures your environment variables
4. Run the *PROJECT-openrc.sh* (replacing PROJECT with your project name) script using the following command
```bash
$ source PROJECT-openrc.sh
```
If your Openstack server is protected by a certificate, add the following line at the end of your PROJECT-openrc.sh file : `export OS_CACERT=/path/to/CertFile.pem`
If you use *OpenStack RC File v3*, you may need to export the following environment variables for Packer to talk to OpenStack using version 2 APIs. You may also add these to the end of your *PROJECT-openrc.sh* script.

```bash
$ export OS_TENANT_NAME=$OS_PROJECT_NAME
$ export OS_TENANT_ID=$OS_PROJECT_ID
$ export OS_DOMAIN_NAME=$OS_USER_DOMAIN_NAME
```

Once you have run the script, you can test your environment by running an OpenStack command, for example, list all images. If you are provided with a list of running instances on your OpenStack project, you can continue.
```bash
$ openstack image list
```

## Provisioning a cluster

#### Step 1. Building a base image

Edit `image/base_image.json` Packer file. The file contains two parts: builders and provisioners. Our version is shown below for reference.

```json
{
  "builders": [
    {
      "type": "openstack",
      "image_name": "Ubuntu 14.04_nist_base",
      "source_image": "<your-source-image-id>",
      "ssh_username": "ubuntu",
      "flavor": "m1.small",
      "networks": ["<your-network-id>"],
      "floating_ip": "<your-floating-ip>",
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

The builders section describes the target platform (OpenStack), the name of our base image (Ubuntu 14.04_nist_base), source image built upon (Ubuntu 14.04 with id bc5e15f8-49dc-484f-9aa0-4252f8867390), and other information needed by Packer to spawn an instance in the OpenStack project. You may need to customized some fields such as id of `source_image`, id of `network`, `floating_ip`, etc. You can find more information at [Packer's OpenStack Builder Documentation](https://www.packer.io/docs/builders/openstack.html). It is useful and convenient to use OpenStack CLI to get the ids of resources, such as `source_image` id and `network` id using the commands below.

```bash
$ openstack image list
$ openstack network list
```

The provisioners section includes steps to configure the instance. Firstly, it calls the `image/install.sh` script to install Ansible. Then, it uses our Ansible Playbooks to install software packages.

The Packer file can be used to build the image using the 'packer build *template*'. It is recommended that you validate the template using 'packer validate *template*'. Below are the commands that you can use to run the Packer file provided. 

Validate your Packer file:
```bash
$ cd image
$ packer validate base_image.json
```

Build your base image:
```bash
$ packer build base_image.json
```
It will take about 20-30 minutes to download and install all the tools including Python, Pip, NumPy, SciPy, Ansible, JDK, Hadoop, Spark, Ganglia, etc.

#### Step 2. Creating a cluster


The cluster spec is defined in the Heat Orchestration Template file `heat-template/hot-template.yaml`. You can edit `heat-template/hot-template.yaml` to customize corresponding parameters for your cluster. The parameters are as follows:
 * The *image* to load on the nodes
 * The *default-flavor* of the instances
 * The number of slaves *slaves-count* and the number of clients *clients-count*
 * The prefixes of the instances: *slaves-basename* and *clients-basename* (slaves and clients are only differentiated by their prefix)
 * The *master-name*
 * The *dns-nameservers* addresses to allow the nodes to access to the Internet, as a comma separated list
 * A boolean parameter to set up the *floating ip address* on the master node. This functionality hasn't been tested yet. So far the best way to link a floating ip to the master node is to do it manually, or to uncomment the `fipass-0:` block line 150
 * The *public_net* label of the public network for which floating IP addresses will be allocated

Customize these parameters by editing the *default values* of the parameters.
```yaml
######## PARAMETERS SECTION STARTS HERE ########
# Parameters to customize the cluster
parameters:

# Default image used by the instances. 
# The EMS system has been tested on Ubuntu 14.04 only so far.
  image:
    type: string
    label: image
    default: Ubuntu 14.04_DSE_base

    [...]


######## PARAMETERS SECTION END HERE ########
```

Create your cluster, called a stack in OpenStack, using the following command.

```bash
$ openstack stack create -t hot-template.yaml mystack
```

Check stack status using the follwoing command. Once the stack is created, the status will change from *CREATE_IN_PROGRESS* to *CREATE_COMPLETED* .

```bash
$ openstack stack show mystack -f json
```

You can also edit the template and update the stack if nessesary using the following command.

```bash
$ openstack stack update -t hot-template.yaml mystack
```

In order to log into your nodes, you will need to get the SSH credentials from OpenStack as follows.

* Log into your OpenStack project Dashboard, and go to *Orchestration* -> *Stacks* ->*Your Stack* -> *Overview*.
* From this panel, copy the private key value listed as *private_ssh_key* and save it into a file.
* SSH requires the private key files to have *special access authorizations*. You can add that using the following command:

```shell
chmod 600 /path/to/your/private-key-file
```

Add this identity to your ssh-agent:

```shell
ssh-add /path/to/your/private-key-file
```

Lastly, the master node has to be associated with a floating IP address in OpenStack. Once that is done, you can connect to your node through ssh using the command below. Note, the _ubuntu_ user name may be different if the image used is not an Ubuntu distribution.

```shell
ssh -A ubuntu@floating-ip-address
```

When you are done, you can delete your stack using following command:
```bash
$ openstack stack delete mystack
```

For more information about how to bring up a cluster using Heat, see 'heat-template/README.md'.

#### Step 3. Configuring the cluster

You can configure the cluster either on your localhost or on the master node of your cluster. We recommend you ssh into the master node and configure your cluster from there since Ansible needs to reach all of your cluster nodes. By doing this, we only need to allocate one floating IP for the master node. We show how to do so below.

If you choose to configure on your master node, copy playbooks to it and SSH to it while forwarding your ssh key:

```bash
$ scp -r ./playbooks ubuntu@master-ip:~
$ ssh -A ubuntu@master-ip
```

Edit `/etc/hosts` file on the master node and add all of the cluster nodes' IP addresses and hostnames since Ansible uses hostnames to connect to the nodes. An example addition would be as follows. You may need to replace the ips and hostnames with your own.

```
...

10.10.0.4 master
10.10.0.6 slave-0
10.10.0.5 slave-1
10.10.0.8 slave-2
10.10.0.7 client-0
```

Edit Ansible inventory file `playbooks/cluster` and add cluster nodes to corresponding categories. An example addition would be as follows. Again, you may need to replace the ips and hostnames with your own.

```yaml
[master]
master ipv4=10.10.0.4

[slaves]
slave-0 ipv4=10.10.0.6
slave-1 ipv4=10.10.0.5
slave-2 ipv4=10.10.0.8

[client]
client-0 ipv4=10.10.0.7

...
```

Once you are done editing the files, you can configure the nodes using the following commands. If there is an error configuring the nodes, you may need to ssh into them and run 'sudo apt-get update && sudo apt-get dist-upgrade' to update their packages before retrying the command.

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

Ansible uses *tags* to select tasks to execute. For more information or to have finer control over tasks, see 'playbooks/README.md'.

#### Step 4. Testing (Optional)

Once the cluster is up and running, it is a good idea to run a task on the cluster to test it. For convenience, we have provided a Hadoop application for calculating Pi for this testing.

```bash
$ ansible-playbook -i cluster --tags hadoop-test client.yml
```

This command will start the application on the client node, which talks to master to schedule its jobs to execute on slaves.

### How to use the cluster

## Contact

## License
