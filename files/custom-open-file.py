import resource
import subprocess
import os
import pwd
import time

from checks import AgentCheck

class OpenFileCheck(AgentCheck):
    def check(self, instance):
        try:
            #TODO LOW move this to another custom check
            try:
                with open('/proc/sys/fs/file-nr', 'r') as file_handle:
                    handle_contents = file_handle.read()
                handle_metrics = handle_contents.split()
                self.gauge('custom.system.fs.allocated_fh', float(handle_metrics[0]))
                self.gauge('custom.system.fs.allocated_unused_fh', float(handle_metrics[1]))
                self.gauge('custom.system.fs.max_fh', float(handle_metrics[2]))
            except Exception:
                self.fail_event('Cannot extract system file handles stats')

            proc_name = instance['process_name_pattern']
            if 'alias' in instance:
                name_tag = instance['alias']
            else:
                name_tag = proc_name
            ps_result, ps_err = subprocess.Popen(
                ['pgrep', '-f', proc_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ).communicate()
            processes = ps_result.split('\n')
            proc_count = 0
            min_soft_limit = None
            max_soft_limit = None
            min_hard_limit = None
            max_hard_limit = None
            if len(processes) > 0:
                for i in range(0, len(processes)):
                    #add try/catch here, in case we can't find the process
                    pid = processes[i]
                    try:
                        if pid:
                            limit_content, limit_content_err = subprocess.Popen(
                                ['grep', 'open files', '/proc/' + pid + '/limits'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            ).communicate()
                            #check for empty or null string
                            if limit_content:
                                parsed_limit_content = list(
                                    filter(None, limit_content.split(' '))
                                )
                                #tags = [ 'pid:' + pid, 'process_name_pattern:' + proc_name ]
                                soft_limit = int(parsed_limit_content[3])
                                hard_limit = int(parsed_limit_content[4])
                                if min_soft_limit:
                                    if min_soft_limit > soft_limit:
                                        min_soft_limit = soft_limit
                                    if min_hard_limit < hard_limit:
                                        min_hard_limit = hard_limit
                                    if max_soft_limit < soft_limit:
                                        max_soft_limit = soft_limit
                                    if max_hard_limit > hard_limit:
                                        max_hard_limit = hard_limit
                                else:
                                    min_soft_limit = soft_limit
                                    max_soft_limit = soft_limit
                                    min_hard_limit = hard_limit
                                    max_hard_limit = hard_limit
                                proc_count = proc_count + 1
                    except:
                        self.fail_event(
                            '[ERROR] failed to get the process information, ' + \
                            'pid: ' + str(pid) + ', process name: ' + proc_name,
                        )
            else:
                if ps_err: #error message is not empty and not null
                    self.fail_with_exception_event(
                        '[ERROR] process name: ' + proc_name,
                        ps_err
                    )
            tags = [ 'process_name:' + name_tag ]
            self.gauge(
                'custom.system.process.count',
                proc_count,
                tags=tags
            )
            self.gauge(
                'custom.system.open_file.soft_limit_min',
                min_soft_limit,
                tags=tags
            )
            self.gauge(
                'custom.system.open_file.soft_limit_max',
                max_soft_limit,
                tags=tags
            )
            self.gauge(
                'custom.system.open_file.hard_limit_min',
                min_hard_limit,
                tags=tags
            )
            self.gauge(
                'custom.system.open_file.hard_limit_max',
                max_hard_limit,
                tags=tags
            )
            #sending this metric to help setting up alerts
            self_proc_result, self_proc_err = subprocess.Popen(
                'ls -l /proc/[0-9]*/fd', shell = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ).communicate()
            proc_lines = self_proc_result.split('\n')
            total_open_by_self = 0
            for line in proc_lines:
                if len(line) > 0 and not (line.startswith('total') or line.startswith('/proc/')):
                    total_open_by_self = total_open_by_self + 1
            self.gauge(
                'custom.system.open_file.ddagent_count',
                total_open_by_self
            )
        except:
            self.fail_event('[ERROR] config: ' + str(instance))

    def fail_with_exception_event(message, exception):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'failure',
            'msg_title': 'Caught exception',
            'msg_text': '%s: %s' % (message, exception)
        })

    def fail_event(message):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'failure',
            'msg_title': 'Failed to get data',
            'msg_text': '%s' % (message)
        })

if __name__ == '__main__':
    check, instances = OpenFileCheck.from_yaml(
        '/etc/dd-agent/conf.d/custom-process.yaml'
    )
    for instance in instances:
        print '\nRunning the check for: %s' % (instance['process_name_pattern'])
        check.check(instance)
        if check.has_events():
            print 'Events: %s' % (check.get_events())
        print 'Metrics: %s' % (check.get_metrics())

