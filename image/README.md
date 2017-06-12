DSE-Image project aims to create base Virtual Machine (VM) images with data
science tools pre-installed for multiple platforms, such as OpenStack, AWS EC2,
VirtualBox and etc by using Packer.

### Prerequisites

* Packer


### How Packer works

Packer requires users to create a packer file in json format which defines the
target platforms and provisioning scripts for your images, namely builders and
provisioners respectively. For instance, defining an OpenStack image based on
Ubuntu 14.04 with flavor Small and provisioned with NumPy and SciPy installed.

Packer builds the image by connecting to the platform, spawning an instance and
running the given provisioning scripts automaticly. Once the provision is done,
Packer stops the instance and create an image of it.

### Creating a base DSE image for OpenStack

#### Download and source OpenStack Project's RC file

The RC file of your project includes your authentication and tenant information
of OpenStack, and can be found at Dashboard -> Compute -> Access & Security
-> API Access -> Download OpenStack RC file.

Source the RC file. you will be required to enter your OpenStack account
password for authentification.
```
$ source my_project_openrc.sh
```

#### Run Packer to build the image

The Packer file (dse_vm.json) defined for base DSE image.

```json
{
  "builders": [
    {
      "type": "openstack",
      "ssh_username": "ubuntu",
      "image_name": "dse_base",
      "source_image": "22a2004b-8cb6-4526-aa87-8fed5b3ad1e5",
      "flavor": "2",
      "networks": ["c18e3d7d-1b38-433e-8fdd-84389291b119"],
      "floating_ip": "192.168.0.2",
      "availability_zone": "nova",
      "insecure": true
    }
  ],

  "provisioners": [
    {
      "type": "shell",
      "script": "install.sh"
    }
  ]
}
```

The file includes one builder for OpenStack specifying the name of the image
(des_base), source image id (22a2004b-8cb6-4526-aa87-8fed5b3ad1e5, Ubuntu
14.04), instance flavor (2, small), network, etc. Since EMS OpenStack uses
self-signed certificate, we use insecure connection. The provisioner points to
a script which installs tools and does the configurations.

Check the format of the Packer file.
```shell
$ packer validate dse_vm.json                                                                                                 148 master?
Template validated successfully.
```

Build an image:
```shell
$ packer build dse_vm.json                                                                                                       master!?
openstack output will be in this color.

==> openstack: Discovering enabled extensions...
==> openstack: Loading flavor: 2
    openstack: Verified flavor. ID: 2
==> openstack: Creating temporary keypair: packer 58ac6935-f1d5-9581-72fe-17fe78e3be69 ...
==> openstack: Created temporary keypair: packer 58ac6935-f1d5-9581-72fe-17fe78e3be69
==> openstack: Successfully converted BER encoded SSH key to DER encoding.
==> openstack: Launching server...
    openstack: Server ID: 35f19a22-a2b7-4f80-8bc7-3acfaa3ab186
==> openstack: Waiting for server to become ready...
==> openstack: Associating floating IP with server...
    openstack: IP: 192.168.0.2
    openstack: Added floating IP 192.168.0.2 to instance!
==> openstack: Waiting for SSH to become available...
==> openstack: Connected to SSH!
==> openstack: Provisioning with shell script: install.sh
...
    openstack: done.
    openstack: done.
==> openstack: Stopping server: 0a69890d-f7e8-427c-b32c-5f1610308ecf ...
    openstack: Waiting for server to stop: 0a69890d-f7e8-427c-b32c-5f1610308ecf ...
==> openstack: Creating the image: dse_base
    openstack: Image: 6661c95f-875e-4fed-bab3-df54dd7230e5
==> openstack: Waiting for image dse_base (image id: 6661c95f-875e-4fed-bab3-df54dd7230e5) to become ready...
==> openstack: Terminating the source server: 0a69890d-f7e8-427c-b32c-5f1610308ecf ...
==> openstack: Deleting temporary keypair: packer 58a76b93-0454-2bfb-5d4d-a022b5d3e3fd ...
Build 'openstack' finished.

==> Builds finished. The artifacts of successful builds are:
--> openstack: An image was created: 6661c95f-875e-4fed-bab3-df54dd7230e5
```

Since lots of tools get installed, it will take more than 10 minutes to build the image.

