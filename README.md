ansible-datadog-configure-custom-open-file-checks

Ansible Role to configure Datadog Agent Custom Open File Checks

It will collect these metrics:
- custom.system.fs.allocated_fh: global allocated file handles
- custom.system.fs.allocated_unused_fh: global allocated but unused file handles
- custom.system.fs.max_fh: global limit of file handles
- custom.system.open_file.ddagent_count: opened file handles from all processes that are run by the user that runs Datadog agent
and these metrics for each "process_name_pattern":
- custom.system.process.count: count of running processes that match the process_name_pattern
- custom.system.open_file.soft_limit_min: the minimum of (soft limit for opening file handles) from all processes that match the process_name_pattern
- custom.system.open_file.soft_limit_max: the maximum of (soft limit for opening file handles) from all processes that match the process_name_pattern
- custom.system.open_file.hard_limit_min: the minimum of (hard limit for opening file handles) from all processes that match the process_name_pattern
- custom.system.open_file.hard_limit_max: the maximum of (hard limit for opening file handles) from all processes that match the process_name_pattern


It's related to this doc: https://docs.datadoghq.com/guides/agent_checks/
This role contains two parts:
- Adding custom open-file checks
- Removing custom open-file checks

Installing / Uninstalling Datadog Custom Open File Checks

For installation, it will add file <custom-check-name>.yaml and <custom-check-name>.py.
For uninstallation, it will remove file <custom-check-name>.yaml and <custom-check-name>.py.

Required Variables

None

Additional Variables
- custom_check_state
  desc: present, absent
  default: present

- check_config:
  desc: The value for <custom-check-name>.yaml, you don't need this if "custom_check_state" is "absent". If you set this, there are 2 attributes that you can specify:
  - "init_config"
    you can set attribute "min_collection_interval" (optional), there is a brief explanation at https://docs.datadoghq.com/guides/agent_checks/#configuration
  - "instances"
    you can set attributes:
    - "process_name_pattern" (mandatory), to filter the process that you want to monitor
    - "alias" (optional), we will include this in the tag and if unset, we will use "process_name_pattern"

Testing

There are 2 options of testing:
- Installation (test_present.yml)
- Uninstallation (test_absent.yml)

To testing using vagrant for those options, use:

TASK='task_name' vagrant up

task_name value : test_present.yml, test_absent.yml
