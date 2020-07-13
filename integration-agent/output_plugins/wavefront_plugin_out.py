#!/usr/bin/python3

# plugin which collects metric
# from the source and returns the result

import socket
import test_classes as classes

class OutputPlugin:
    def __init__(self, context):
        self.context = context
        self.config = self.context.get_config()
        self.mode = self.config.get("wf.mode", "proxy")     # [proxy|direct] - default is proxy
        self.host = self.config.get("wf.proxy.host", "localhost")
        self.port = self.config.get("wf.proxy.port", 2878)
        self.prefix = self.config.get("wf.prefix","")
        self.debug = self.config.get("debug") == "true"
        return

    def setup(self):
        return

    def run(self, run_result: classes.RunResult):
        largest_time = 0
        smallest_time = 0
        wf_lines = []
        for m in run_result.metrics:
            l = "{0} {1} {2} source={3}".format(m.name, m.value, m.timestamp, m.source)
            for k, v in m.tags.items():
                tag = " {0}=\"{1}\"".format(k, v)
                l = l + tag
            if self.prefix != "":
                l = "{0}.{1}".format(self.prefix, l)
            if m.timestamp > largest_time:
                largest_time = m.timestamp
            if smallest_time == 0:
                smallest_time = m.timestamp
            elif smallest_time > m.timestamp:
                smallest_time = m.timestamp
            # now ready to put it into lines
            wf_lines.append(l)
        # now, output to wavefront
        self.to_wf_proxy(wf_lines)
        run_result.start_time = smallest_time
        run_result.end_time = largest_time
        return

    # if in debug mode, output to standard output
    def to_wf_proxy(self, wf_lines):
        if self.debug is False:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            for line in wf_lines:
                s.send(line + "\n")
            s.close()
        else:
            for line in wf_lines:
                print(line)