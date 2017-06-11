## AutoPro

AutoPro, short for Automate Provision, defines an automate workflow of configuring large and ready to use OpenStack clusters from scratch by using existing tools and pre-defined templates. It has been developed by the EMS team of IAD group at National Institute of Standards and Technology (NIST), with our experience of evaluating data science projects which rely on large Hadoop, Spark clusters heavily.

The automate workflow has three steps:

1. Building a base image;
2. Creating a OpenStack cluster;
3. Configuring cluster nodes and bringing up services.

The first setup is optional. But a pre-baked base image that has many pre-installed software packages can be reused afterwards, therefore, will save a lot of time.

To implement the workflow, we use multiple tools including Packer, OpenStack Heat as well as Ansible, and has defined corresponding templates in three modules: image, heat_template and playbook. The followings are overviews of these modules, detailed explanations can be found in corresponding subdirectory.

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

Learned from best practices, we categorize cluster nodes into different roles: master, slave, client, and optionally storage. Each cluster can has one master (or multiple to avoid single point failure), many slaves/workers and many clients. A master node runs as a job scheduler or controller; Slaves nodes run jobs assigned to it by master; Users' applications reside in client nodes and talks a the master node to get resources from cluster and execute their jobs.

We also support to provision a single node cluster which itself acts as master, slave and client at the same time.

## Get started

We are going to provision a cluster consisting of a master, a client and three slave nodes. The cluster runs Hadoop, Spark, Ganglia, NFS and NTP. At the end, we will run a Hadoop application calculating Pi using quasi-Monte Carlo method on the cluster.

### Prerequisites & installation

### Provisioning a cluster

#### Building a base image

Specifically, we've created a Packer file named `dse_vm.json` under image directory which contains two parts: builder and provisioner. The builder part defines base image name, target platform (in this case, OpenStack), and some other info that will be used to create an instance on target platform. The provisioner part includes steps of configuring the instance. Firstly, it calls `image/install.sh` script to install Ansible. After that, it uses our Ansible playbooks to install software packages.

#### Creating a cluster

#### Configuring the cluster

#### Testing

### How to use the cluster

## Contact

## License
