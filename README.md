## Conducere

Conducere, latin for conductor, defines an automated workflow for configuring large, ready-to-use OpenStack clusters using open-source tools and predefined templates. It has been developed by the Evaluation Management System team of the Information Access Division at the National Institute of Standards and Technology (NIST) based on our experience evaluating data science projects that rely heavily on large Hadoop and Spark clusters.

The Conducere workflow has three steps:

1. Build a base image
2. Create an OpenStack cluster
3. Configure cluster nodes and bring up services

Note: The first step is optional, but a pre-baked base image with many pre-installed software packages that can be reused afterwards will save time later on.

To implement the workflow, we used multiple tools including Packer, OpenStack Heat, and Ansible. To do so, we have defined corresponding templates for each of these three tools which are available in the three modules provided in this repository: Image, Heat_template, and Playbooks. While we have written these modules to work together for this project, they can also be used independently if necessary. For example, one could use only the Playbooks module to configure an existing cluster. Brief overviews of these three modules can be found below with more detailed descriptions available in their respective subdirectories.

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

Learning from best practices, we categorize cluster nodes into different roles: master, slave, client, and, optionally, storage. Each cluster can have one master (or multiple to avoid having a single point of failure), many slaves/workers, and many clients. A master node functions as a job scheduler or controller for the cluster. Slave nodes are workers that run jobs assigned to them by the master. Client nodes handle user applications and talk to the master node to procure necessary cluster resources and schedule jobs. The cluster need not follow this format. For example, we also support provisioning a single node cluster which simultaneously acs as a master, slave, and client. Currently, our Playbooks have been tested on Ubuntu 14.04. A few changes may be needed for compatibility with later Ubuntu versions.

## To start using Conducere

See our [getting started](/docs/getting_started.md) documentation.

## Support

If you have any question about Conducere or have a problem using it, you can either file an issue or reach any of following points of contacts.

* Lizhong Zhang   <lizhong.zhang@nist.gov>
* Maxime 	Hubert  <maxime.hubert@nist.gov>
* Martial Michel  <martial.michel@nist.gov>
