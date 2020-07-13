#!/usr/bin/python3

# plugin which collects metric
# from the source and returns the result

import test_classes as classes

class OutputPlugin:
    def __init__(self, context):
        self.context = context
        self.config = self.context.get_config()
        self.server = self.config.get("output.server", "localhost")
        self.port = self.config.get("output.port", 2878)
        self.prefix = self.config.get("output.prefix","")
        return

    def setup(self):
        return

    def run(self, run_result: classes.RunResult):
        return