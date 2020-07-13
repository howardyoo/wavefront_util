#!/usr/bin/python3

# plugin which collects metric
# from the source and returns the result
import time
import test_classes as classes

class InputPlugin:
    def __init__(self, context):
        self.context = context
        self.config = self.context.get_config()
        self.source = self.config.get("read.source", "source")
        return

    def setup(self):
        # setup connections, or access to source, etc.
        return

    def run(self):
        # these are just a test data
        result = classes.RunResult()
        m = classes.Metric("my.metric.test", "source1", 0.001)
        m.tags = {"key1": "val1", "key2": "val2"}
        result.metrics.append(m)

        m = classes.Metric("my.metric.test2", "source2", 11.0)
        m.timestamp = 12345
        result.metrics.append(m)

        result.iteration = len(result.metrics)
        return result