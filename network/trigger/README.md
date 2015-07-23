Trigger is a toolkit used to connect to network devices. While Trigger can utilize a device's API, its main use with Ansible would be to interface with devices for which the only connection methods are telnet or ssh.

You can install trigger through pip or follow on github (http://github.com/trigger).

Read the docs: http://triggerproject.org/en/latest/

##Example

```
- name: Show Version
  hosts: testing
  connection: local
  gather_facts: no

  tasks:
  - name: show version
    trigger_command:
      device={{inventory_hostname}}
      command="show version"
      username="bob"
      password="ih8p@sswds"
    register: trigger

  - name: Display Version Info
    debug:
      var=trigger
```
