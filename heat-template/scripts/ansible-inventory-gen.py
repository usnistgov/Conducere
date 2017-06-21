import sys
import os
import subprocess
import json
import re
import jinja2

# This script generates an inventory of a cluster generated with the heat template file
# This inventory file may then be used by the ansible playbooks
# This script requirements are listed at ./requirements.txt
# Usage:
#       ansible-inventory-gen.py <stack-name>
#
# The generated ./cluster file may then replace the ../playbooks/cluster file

# Detect the environment variables used by the Openstack CLI
if os.environ.get('OS_USERNAME') != None:

    # Detect if the name of the stack is provided
    if len(sys.argv) != 2:
        print '\n  Usage:\n\n    python ansible-inventory-gen.py <stack-name> \n'
    else:
        # Load the json output of openstack stack show
        jsonCall = json.loads(subprocess.check_output('openstack stack show ' + sys.argv[1] + ' -f json -c outputs', shell=True ))

        # For each group of instances, create a {header, output_name, [ {names, addresses} , ... ]} set
        configSet = {'conf':[{'header':'dse_master', 'output_name':'master-name', 'config_lines':[]},
        {'header':'dse_slaves', 'output_name':'slaves-ids', 'config_lines':[]},
        {'header':'dse_clients', 'output_name':'clients-ids', 'config_lines':[]}]}

        print "\n  Loading...\n"

        # Loop on the groups of instances
        for configPair in configSet['conf']:

            # Loop on the json output
            for output in jsonCall['outputs']:

                # If a key in the json output matches the output_name in the configuration set
                if output['output_key']==configPair['output_name']:

                    # Get the server ids of the current group (master-name, clients-ids, slaves-ids)
                    if type(output['output_value']) is unicode:
                        serverIds = [output['output_value']]
                    else:
                        serverIds = output['output_value']

                    # Loop over the ids
                    for serverId in serverIds:

                        # Fetch the names for each id and append it to the configuration set
                        configPair['config_lines'].append(
                        {
                            'name' : subprocess.check_output('openstack server show ' + serverId + ' -f value -c name', shell=True).replace('\n', '') ,
                            'address' : re.search('=(([0-9]+\.)+[0-9])', subprocess.check_output('openstack server show ' + serverId + ' -f value -c addresses', shell=True)).group(1)
                        })

        # Write the cluster configuration file at ./cluster using the templates/cluster.j2 template file
        with open('cluster','w') as outputFile:
            outputFile.write(jinja2.Environment(loader=jinja2.FileSystemLoader('./templates/')).get_template('cluster.j2').render(configSet))
            outputFile.close()

        print "Cluster configuration file written at ./cluster"

else:

    print '\n  Openstack environment variables undefined. \n  Execute the following:\n\n    source path/to/openrc.sh   \n'
