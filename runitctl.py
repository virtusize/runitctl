#!/usr/bin/env python

import cmd
from os import listdir
from os.path import isdir, join
from time import strftime, gmtime

class SV:

    STATE = {'run': 'RUNNING', 'down': 'STOPPED'}

    def __init__(self, dir):
        self.dir = dir
        self.reread()

    def __run_cmd(self, cmd):
        import subprocess
        return subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE).communicate()[0].strip()

    def start(self, service):

        st = self.__run_cmd(['sv', 'start', service])

    def stop(self, service):
        st = self.__run_cmd(['sv', 'stop', service])

    def statuses(self):
        # self.reread()
        return [self.status(s) for s in self.services]

    def reread(self):
        self.services = [f for f in listdir(self.dir) if isdir(join(self.dir, f))]

    def status(self, service):
        import re
        pattern = re.compile(r"""
                            ^(?P<status>[^:]+):\s+
                            (?P<service>[^:]+):\s+
                            (:?\(pid\s+(?P<pid>\d+)\)\s+)?(?P<uptime>\d+)s
                            """, re.VERBOSE)
        st = self.__run_cmd(['sv', 'status', service])
        m = pattern.match(st)
        if m:
            service = m.groupdict()
            return service
        else:
            print "Unknown format"

    def __str__(self):
        out = []
        for s in self.statuses():
            st = self.STATE[s['status']];
            if s['status'] == 'run':
                up = strftime("%H:%M:%S", gmtime(float(s['uptime'])))
                out.append('{: <32} {: <10} pid {}, uptime {}'.format (s['service'], st, s['pid'], up))
            elif s['status'] == 'down':
                since = strftime("%b %d %I:%M %p", gmtime(float(s['uptime'])))
                out.append('{: <32} {: <10} {}'.format(s['service'], st, since))
            else:
                print "Unknown state"
        return '\n'.join(out)

class Controller(cmd.Cmd):

    prompt = 'supervisor> '
    sv = SV('/etc/service')

    def do_help(self, line):
        print "help"

    def do_status(self, line):
        print self.sv

    def do_reread(self, line):
        self.sv.reread()
        print "No config updates to processes"

    def do_stop(self, line):
        self.sv.stop(line)
        print "%s: stopped" % line

    def do_start(self, line):
        self.sv.start(line)
        print "%s: started" % line

    def do_restart(self, line):
        self.do_stop(line)
        self.do_start(line)

    def do_update(self, line):
        pass

    def do_exit(self, line):
        return True

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
            Controller().onecmd(' '.join(sys.argv[1:]))
    else:
        Controller().cmdloop()
