# Overview

This tutorial provides information and advises to deploy a distributed architecture using :

* Openstack CLI client - The CLI client to interact with your Openstack installation.
* Openstack Horizon - The GUI to interact with your Openstack installation.
* Openstack Heat - A tool to build architectures from YAML files.


This document is splited in four main parts :
 * Openstack client installation
 * Cluster orchestration from a template
 * SSH configuration
 * Troubleshooting and further information

****

# Openstack client installation
The installation of the CLI client is not required to install your architecture, but it offers an access to all the administration functions.
## Install and configure the Openstack CLI Client

* Download and install the Openstack and Heat clietns packages using pip:

```shell
pip install python-openstackclient python-heatclient
```


 Follow [this guide](https://docs.openstack.org/user-guide/common/cli-install-openstack-command-line-clients.html) for more information about the clients installation.
* Configure your environment variables :
  * Log into your Openstack Horizon interface.
  * From the Dashboard, go to __Project__ -> __Access & Security__ -> **API Access**
  * Click __Download OpenStack RC File v2.0__ to get the _PROJECT-openrc.sh_ script that configures your environment variables for the Openstack CLI.
  * If your Openstack server is protected by a certificate, add this line at the end of your _PROJECT-openrc.sh_ file : `export OS_CACERT=/path/to/CertFile.pem`
* Run the CLI
  * Execute the _PROJECT-openrc.sh_ file from a terminal using the following :

 ```shell
 source ./PROJECT-openrc.sh
 ```
  * When prompted, enter the password of the user who downloaded the script file.

At this point, **your environment is configured in the current terminal**. You can now run :

```shell
openstack help
```
The two substeps of __Run the CLI__ must be executed on **any terminal** from which you want to run the Openstack client.

****
# Cluster orchestration from a template
## Outline
This part gives the outline for configuring a small cluster architecture using the provided __Heat Orchestration Template__ (HOT).
For more details about Heat templates, [check the full documentation](https://docs.openstack.org/developer/heat/template_guide).

The template file is configuring the following :
  * One **router** called `rt-0`
  * A **network** `net-0`
  * A **subnet** `subnet-0` with a _10.10.0.0/24_ address spacing
  * A **security group** `sgroup-0` that allows ssh connection from the outside, and any connection between the members of this server
  * An **interface** `rt-if-0` between the subnetwork and the router
  * A **floating IP** `fip-0` to be able to ssh to a node using a public IP address. **This setting is disabled by default**. To activate it, uncomment the `fipass-0` block line 150.

* Five **nodes** running *Ubuntu 14.04*
  * One node called `master` that can be associated with the floating ip address mentioned above
  * Three slave nodes called `slave-0`, `slave-1`, and `slave-2`
  * One client called `client-0`


* A **ssh-key** to be installed on each node

The network structure can be described as following :

![Cluster architecture schema](./schema/1ms-2sl-shema.png?raw=true "Cluster architecture schema")

## The Heat Orchestration Template file
This Heat Orchestration File is used as an input for the Heat module from Openstack. The Heat module allows us to create a stack : a full configuration of a cluster architecture.
This section introduces the content of the provided YAML file. The indentation inside of the structure is made with multiples of two spaces, and the lines are commented with the `#` character.
The first line of the YAML file refers to the version of the Heat Template. According to your version, some functions may not be available.  
See [this page](https://docs.openstack.org/developer/heat/template_guide/hot_spec.html#heat-template-version) for more information about template versions.

### File structure
The template file is structured this way:
```yaml
heat_template_version: yyyy-mm-dd
description: the description of the template
parameters:
  [...] These parameters are customizable
resources:
  [...] Resources list
outputs:
  [...] Parameters used to monitor the stack
```
The customizable parameters are available in the `parameters:` section.

## Stack management
This section introduces how to use the CLI to launch the provided YAML file.
Please follow [this page](https://docs.openstack.org/user-guide/cli-create-and-manage-stacks.html) to get more information about stack management using the CLI.
Execute `openstack -h your command` to print the  manual of this command.

### Create a new stack from the template file
In order to deploy your architecture, your Openstack environment variables must be set in your terminal. In order to build a stack using tis template with custom parameters, use the following command:

```shell
openstack stack create -t /path/to/file.yaml <stack-name> --parameter="key1=value1" --parameter="key2=value2"
```

The following parameters are customizable.
 * The **image** label to load on the nodes.
 * The **default-flavor** of the instances.
 * The number of slaves **slaves-count** and the number of clients **clients-count** (slaves and clients are only differentiated by their prefix)
 * The prefixes of the instances: **slaves-basename** and **clients-basename**
 * The **master-name**.
 * The **dns-nameservers** addresses to allow the nodes to access to the Internet, as a comma separated list.
 * A boolean parameter to set up the **floating ip address** on the master node. This functionality hasn't been tested yet. So far the best way to link a floating ip to the master node is to do it manually, or to uncomment the `fipass-0:` block line 150.
 * The **public_net** label of the public network for which floating IP addresses will be allocated.

An **easier way** to use this template with custom parameters is to **change the default values** of the parameters in the `parameters:` section in the template.

### Get a stack status
Execute this command to get the status of your stack. This command also provides the values of the `output:` section in the YAML file. In case of an error, please follow the instructions at the **Troubleshooting** section.

```shell
openstack stack show <stack-name>
```

### Delete a stack
The stack deletion operation deletes all the resources in the stack.  

```shell
openstack stack show <stack-name>
```

### Update a stack
Heat supports stacks **updates**. It is possible to create new nodes on a current stack only by updating the YAML template for example.

```shell
openstack stack update -t /path/to/new-file.yaml <stack-name>
```


****
# SSH configuration

This part explains how to set up SSH to access any node that has been brought up automatically.

## Get the generated private key

* From the Dashboard, go to **Orchestration** -> __Stacks__ ->__Your Stack__ -> **Overview**
* From this panel, copy the private key value listed as **private_ssh_key**.
* Save it into a new file, or append it to `/home/you/.ssh/id_rsa`
* SSH requires the private key files to have **special access authorizations**. Set it using the following :

```shell
chmod 600 /path/to/your/private-key-file
```
## Connect to a node
**The Floating IP configuration is disabled by default** in this template. To activate it, uncomment the `fipass-0` block line 150 and update your stack **or** attach a floating ip address to an existing instance using the __Attach floating ip__ action available in the instance list at __Project__ -> __Instances__.
You should now be able to connect using ssh to a node attached to a *floating-ip-address* using the following command :

(The `-i` option is required only if you did not save the private key to `/home/you/.ssh/id_rsa`. Also, the _ubuntu_ user name may be different if the image used is not an Ubuntu distribution).
```shell
ssh ubuntu@floating-ip-address -i /path/to/your/private-key-file
```

**Done !** You should now be connected to a node. You are now able to install the [dse-ansible](https://gitlab.nist.gov/gitlab/ems/dse-ansible) environment.

`Note :` If you are using a *ssh-agent*, you may want to use this command:
```shell
eval "$(ssh-agent -s)"
ssh-add /path/to/your/private-key-file
```
****
## More information

### Troubleshooting
This section aims to guide in case of error. Usually, errors occurring during the stack management operations return a `CREATE_FAILED`, `UPDATE_FAILED`, or `DELETE FAILED`.
To get more information about an error, use the following command:
```shell
openstack stack show <stack-name> -c stack_status_reason
```

This section explains the most common error, and how to solve it.  
#### Common causes of CREATE_FAILED errors

##### It is highly recommended to delete a stack that failed before trying to create it again.
<br/>
 * **OverQuotaClient:Quota exceeded for resources RESOURCE_NAME**:
This type of error appears if Heat didn't find enough resources to build the stack. Try to delete some existing resources or ask your Openstack administrator to provide some more.

#### Common causes of DELETE_FAILED errors
The error description will provide information about the resources that cause conflicts during the deletion. Delete these resources manually using the GUI or the CLI and delete the stack again.


### Template customization guide
Some more customization of this template may be required. Here's a quick introduction to understand the heat template syntax.
The following structure configures the master node: a Nova `OS::Nova::Server` resource.

```yaml
# Master node instance
  master-node:
    type: OS::Nova::Server
    properties:
      name: { get_param: master-name }
      availability_zone: nova
      key_name: { get_resource: sshk-0 }
      image: { get_param: image }
      flavor: { get_param: default-flavor }
      security_groups: [{ get_resource: sgroup-0 }]
      networks:
        - port: { get_resource: port-master }
```

Each node is configured this way, using a `get_resource` function to link it to other resources, and a `get_param` function to get the values from the `parameters:` section.

As an example, the `key_name` property of the resource **links** to this `OS::Nova::KeyPair` resource :
```yaml
  sshk-0:    
  type: OS::Nova::KeyPair
  properties:     
    name: sshk-0
    save_private_key: true
```
After the ssh key pair is created, the private key associated with this public key is available thanks to the `save_private_key: true`, and defining this structure in the `outputs:` section of the document:
```yaml
outputs:
  private_ssh_key:     
  description: Private ssh key to access nodes.     
  value: { get_attr: [sshk-0, private_key] }
```

This output value will be available as an output of the future stack.
You can add even more features to this template. To get more examples, check this [Openstack Github repository](https://github.com/openstack/heat-templates/tree/master/hot). And to get the full documentation, [check this link](https://docs.openstack.org/developer/heat/template_guide/openstack.html).
