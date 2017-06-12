#!/bin/bash

# Wait and make sure Ubuntu properly initialize
sleep 10

# Install Ansible
#sudo apt-get update
#sudo apt-get -y install python-dev python-pip
#sudo pip install ansible

sudo apt-get update
sudo apt-get install -y software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -y ansible
