Trigger is a toolkit used to connect to devices. While Trigger can utilize a device's API, its main use with Ansible would be to interface with devices for which the only connection methods are telnet or ssh.


You can install trigger through pip or follow on github (http://github.com/trigger).

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

  - name: Display Pre-Change BGP Information
    debug:
      var=trigger
```
