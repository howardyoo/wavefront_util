#!/usr/bin/python3

import test_classes as classes

class PreProcessor:
    def __init__(self, context):
        self.context = context
        self.config = self.context.get_config()
        return

    def setup(self):
        return

    def run(self, result: classes.RunResult):
        return result