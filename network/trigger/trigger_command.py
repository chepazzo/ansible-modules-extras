#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Mike Biancaniello <chepazzo@gmail.com> <m.biancaniello@teamaol.com>
#
# This file is a module for Ansible that interacts with Trigger
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.    If not, see <http://www.gnu.org/licenses/>.


DOCUMENTATION = """
---
module: trigger_command
short_description: Sends arbitrary commands to devices via the Commando API
description:
  - The trigger_command module provides a module for sending arbitray
    commands to a node and returns the ouput. 
version_added: 0.0.0
category: System
author: Mike Biancaniello (@chepazzo)
requirements:
  - Commando API 0.3.3 or later installed on remote server
  - trigger>=1.5.2
notes:
  - This module does not support idempotent operations.
  - This module does not support stateful configuration
options:
  command:
    description:
      - Specifies the command to send to the node and execute
        in the configured mode.
    required: true
    version_added: 0.0.0
  device:
    description:
      - Specifies the devicename on which to execute the commands.
    required: true
    version_added: 0.0.0
  username:
    description:
      - Specify the username
    required: false
    default: null
    version_added: 0.0.0
  password:
    description:
      - Specify the password
    required: false
    default: null
    version_added: 0.0.0
"""

EXAMPLES = """

  - name: show version
    trigger_command:
      device={{inventory_hostname}}
      command="show version"
      username="bob"
      password="ih8p@sswds"
    register: trigger

"""

try:
    from trigger.cmds import Commando
    TRIGGER_AVAILABLE = True
except ImportError:
    TRIGGER_AVAILABLE = False

PROD_ONLY = False
TIMEOUT = 30
VERBOSE = True
DEBUG = True

class Do(Commando):
    def __init__(self, commands=[], debug=False, timeout=TIMEOUT, **args):
        '''
        adding files,debug to allowed arguments
        '''
        #print "\n\nDEBUG: "+str(debug)
        self.commands = commands
        self.data = {}
        self.debug = debug
        if 'args' in locals():
            args['timeout'] = timeout
        else:
            args = dict(timeout=timeout)
        Commando.__init__(self, **args)

def send_command(module):
    d = module.params['device']
    c = module.params['command']
    creds = None
    if 'username' in module.params and 'password' in module.params:
        u = module.params['username']
        p = module.params['password']
        creds = (u,p)
    try:
        n = Do(devices=[d], commands=[c], creds=creds, verbose=VERBOSE, debug=DEBUG, timeout=TIMEOUT, production_only=PROD_ONLY)
    except Exception as e:
        module.fail_json(msg=str(e))
        return False
    ## run() will send the commands to the device.
    n.run()
    data = n.results[d]
    module.exit_json(changed=True,changes=data)

def main():
    argument_spec = dict(
        device=dict(required=True),
        command=dict(required=True),
        username=dict(required=False, default=None),
        password=dict(required=False, default=None)
    )
    module = AnsibleModule(argument_spec=argument_spec)
    if not TRIGGER_AVAILABLE:
        module.fail_json(msg='trigger is required for this module. Install from pip: pip install trigger.')
    send_command(module)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

