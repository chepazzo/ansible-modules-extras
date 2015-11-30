#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Mike Biancaniello <chepazzo@gmail.com> <m.biancaniello@teamaol.com>
#
# This file is a module for Ansible that interacts with Trigger
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.    If not, see <http://www.gnu.org/licenses/>.


DOCUMENTATION = """
---
module: trigger_command
short_description: Sends arbitrary commands to devices via the Trigger framework
description:
  - The trigger_command module provides a module for sending arbitray
    commands to a network node and returns the ouput. 
  - Trigger is a toolkit used to connect to network devices. While Trigger can utilize a device's API, its main use with Ansible would be to interface with devices for which the only connection methods are telnet or ssh.
  - You can install trigger through pip or follow on github (http://github.com/trigger).
  - Read the docs: http://triggerproject.org/en/latest/
version_added: "1.9"
category: network
author: Mike Biancaniello (@chepazzo)
requirements:
  - trigger>=1.5.2
notes:
  - This module does not support idempotent operations.
  - This module does not support stateful configuration
options:
  command:
    description:
      - Specifies the command to execute on the node.
    required: true
  device:
    description:
      - Specifies the devicename on which to execute the commands.
    required: true
  username:
    description:
      - Specify the username. If omitted, Trigger will try to figure it out.
    required: false
    default: null
  password:
    description:
      - Specify the password. If omitted, Trigger will try to figure it out.
    required: false
    default: null
"""

EXAMPLES = """

  - name: show version
    trigger_command:
      device={{inventory_hostname}}
      command="show version"
      username="bob"
      password="ih8p@sswds"
    register: trigger_show_version

"""

try:
    from trigger.cmds import Commando
    TRIGGER_AVAILABLE = True
except ImportError:
    TRIGGER_AVAILABLE = False

TIMEOUT = 30
VERBOSE = True
DEBUG = True
## Whether or not to restrict devices to production.
## See Trigger documentation for netdevices.
PROD_ONLY = False
## Whether or not to force using the cli for Juniper devices.
## If False, then you have to write a handler to parse the xml output.
FORCE_CLI = True

class Do(Commando):
    '''
    A Commando subclass to instantiate the command(s) to be run.

    Args:
      commands (list): A list of commands (str) to be run on specified devices.
      devices (list): A list of devices on which to run specified commands.
      creds (Optional(tuple)): A tuple containing (username,password) for authenticating
        on the devices.
        | If omitted, Trigger will try to figure it out
        | See Trigger documentation for netdevices.
        | Default is None.
      timeout (Optional[int]): Timeout (in sec) to wait for a response from the device.
        | Default is 30.

    '''
    def __init__(self, commands=None, debug=False, timeout=TIMEOUT, **args):
        if commands is None:
            commands = []
        #print "\n\nDEBUG: "+str(debug)
        self.commands = commands
        self.data = {}
        self.debug = debug
        if 'args' in locals():
            args['timeout'] = timeout
        else:
            args = dict(timeout=timeout)
        Commando.__init__(self, **args)

def send_command(d,c,creds):
    '''
    Sends a command to a device.

    Args:
      d (str): Name of device on which to run specified command.
      c (str): Command to run on specified device.
      creds (tuple): A tuple containing (username,password) for authenticating
        on the devices.

    Returns:
        str: Text output from device.
    '''
    try:
        n = Do(devices=[d], commands=[c], creds=creds, verbose=VERBOSE, debug=DEBUG, timeout=TIMEOUT, production_only=PROD_ONLY,force_cli=FORCE_CLI)
    except Exception:
        return None
    ## run() will send the commands to the device.
    n.run()
    data = n.results[d]
    return data

def module_main(module):
    '''
    Main Ansible module function.
    This just does Ansible stuff like collect/format args and set 
    value of changed attribute.
    '''
    d = module.params['device']
    c = module.params['command']
    creds = None
    if 'username' in module.params and 'password' in module.params:
        u = module.params['username']
        p = module.params['password']
        creds = (u,p)
    data = send_command(d,c,creds)
    if data is None:
        module.fail_json(msg='Command failed.')
        return False
    module.exit_json(results=data)

def main():
    '''
    Main function for python module.
    '''
    argument_spec = dict(
        device=dict(required=True),
        command=dict(required=True),
        username=dict(required=False, default=None),
        password=dict(required=False, default=None)
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )
    if not TRIGGER_AVAILABLE:
        module.fail_json(msg='trigger is required for this module. Install from pip: pip install trigger.')
    module_main(module)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

