## Conducere

Conducere, latin for conductor, defines an automated workflow for configuring large, ready-to-use [OpenStack](https://www.openstack.org/) clusters using open-source tools and predefined templates.
It has been developed by the Evaluation Management System (EMS) team of the [National Institute of Standards and Technology](https://www.nist.gov/) (NIST)'s [Information Technology Laboratory](https://www.nist.gov/itl) (ITL)'s [Information Access Division](https://www.nist.gov/itl/iad) (IAD)'s [Multimodal Information Group](https://www.nist.gov/itl/iad/mig) (MIG), based on our experience evaluating data science projects that rely heavily on large [Hadoop](https://hadoop.apache.org/) and [Spark](https://spark.apache.org/) clusters.

The Conducere workflow has three steps:

1. Build a base image
2. Create an OpenStack cluster
3. Configure cluster nodes and bring up services

Note: The first step is optional, but a pre-configured base image with many pre-installed software packages that can be reused afterwards will save time later on.

To implement the workflow, we used multiple tools including [Packer](https://www.packer.io/), [OpenStack Heat](https://wiki.openstack.org/wiki/Heat) and [Ansible](https://www.ansible.com/). To do so, we have defined corresponding templates for each of these three tools which are available in the three modules provided in this repository: `image`, `heat-template`, and `playbooks`. While we have written these modules to work together for this project, they can also be used independently if necessary. For example, one could use only the `playbooks` module to configure an existing cluster. Brief overviews of these three modules can be found below with more detailed descriptions available in their respective subdirectories.

#### `image` Module

[Packer](https://www.packer.io/) is an open-source tool used to automate the creation of different types of Virtual Machine (VM) images (for [OpenStack](https://www.openstack.org/), [AWS EC2](https://aws.amazon.com/ec2/), [Google Compute Engine](https://cloud.google.com/compute/), [Oracle VirtualBox](https://www.virtualbox.org/), etc). We use `Packer` to build our base image. It builds an image by connecting to the target platform, spawning an instance, and running the given provisioning scripts automatically. Once the provisioning is done, `Packer` stops the instance and saves its image. We've defined a `Packer` file named `dse_vm.json` under the `image` subdirectory that contains information about the target platform (OpenStack in this case), meta information of our target image, and references to our configuration scripts.

#### `heat-template` Module

[OpenStack Heat](https://wiki.openstack.org/wiki/Heat) provides a template based orchestration of an OpenStack cluster. In our Heat template, we describe our desired cluster specifications, including:
* compute resources: number of nodes and, for each node, its flavor (number of CPUs, memory size and disk size)
* network configuration: router, network interfaces, and network access rules
* node configuration: desired image for the nodes (e.g. [Ubuntu](https://www.ubuntu.com/) 14.04 cloud image or customized base image).

#### `playbooks` Module

[Ansible](http://docs.ansible.com/ansible/index.html) is an automated system configuration tool. `Ansible` uses *Playbooks* as configuration, deployment, and orchestration language. Playbooks instruct `Ansible`'s modules on how to configure the remote machines. `Ansible` modules are the building blocks that can be executed directly on remote hosts or through Playbooks. `Ansible` ships with a number of modules managing systems' software packages, services, files, and more.

We've created a custom Playbooks configuration to provision clusters specifically for data science projects. Currently, we support provisioning of:

- [Hadoop](https://hadoop.apache.org/)
- [Spark](https://spark.apache.org/)
- [Ganglia](http://ganglia.sourceforge.net/)
- [NFS](https://en.wikipedia.org/wiki/Network_File_System)
- [NTP](http://www.ntp.org/)
- [DMoni](https://github.com/usnistgov/DMoni)
- [Python](https://www.python.org/) 2.7, including [NumPy](http://www.numpy.org/), [SciPy](https://www.scipy.org/), or [Scikit-learn](http://scikit-learn.org/stable/) among others.

For complex, distributed frameworks and tools, such as Hadoop, Spark, Ganglia, NFS, NTP, and DMoni, Playbooks are included in corresponding subdirectories.

Learning from best practices, we categorize cluster nodes into different roles: master, worker, client, and, optionally, storage. Each cluster can have one master (or multiple to avoid having a single point of failure), many workers, and many clients.

A master node functions as a job scheduler or controller for the cluster. 
Worker nodes run jobs assigned to them by the master. 
Client nodes handle user applications and talk to the master node to procure necessary cluster resources and schedule jobs.

The cluster need not follow this format. For example, we also support provisioning a single node cluster which simultaneously acs as a master, worker, and client. 

Currently, our Playbooks have been tested on Ubuntu 14.04. A few changes may be needed for compatibility with later Ubuntu versions or other [Linux](https://www.linuxfoundation.org/) distributions.

## To start using Conducere

See our [getting started](/docs/getting_started.md) documentation.

## Support

If you have any question about Conducere or have a problem using it, please email [ems_poc@nist.gov](mailto:ems_poc@nist.gov).

## Contributors

* Lizhong Zhang ✻
* Maxime Hubert ✻
* Lukas Diduch ✾
* Jim Golden ❖
* Peter Fontana ❖
* Pooneet Thaper ✷
* Krunal Puri ❄
* Ahmad Anbar ❄
* Olivier Serres ❄
* Martial Michel ❖ Project Lead

( ❖ NIST / ✻ Guest Researcher / ✾ Contractor / ✷ Student / ❄ Former Contributor )

## Disclaimer

Certain commercial entities, equipment, or materials may be identified in this document in order to describe an experimental procedure or concept adequately. Such identification is not intended to imply recommendation or endorsement by the National Institute of Standards and Technology, nor is it intended to imply that the entities, materials, or equipment mentioned are necessarily the best available for the purpose.
All copyrights and trademarks are properties of their respective owners.