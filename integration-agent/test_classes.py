#!/usr/bin/python3

import time
import test_utility as util

class Metric:
    def __init__(self, name, source, value, timestamp=int(time.time()), tags={}):
        self.name = name
        self.source = source
        self.value = value
        self.timestamp = timestamp
        self.tags = tags

class RunResult:
    def __init__(self, run_name="run_result"):
        self.name = run_name
        self.iteration = 0
        self.metrics = []       # array type of Metric
        self.start_time = 0
        self.end_time = 0

class Config:
    def __init__(self):
        self.name = "config"
        self.configFile = "agent.properties"
        # load the config
        self.config = util.load_properties(self.configFile)
        self.pollInterval = self.config.get("pollInterval", 0)
        self.pollLimit = self.config.get("pollLimit", 1000)
        self.inputType = self.config.get("inputType", "")
        self.outputType = self.config.get("outputType", "")
        self.processorType = self.config.get("processorType", "")
        self.startTime = self.config.get("startTime", 0)
        self.endTime = self.config.get("endTime", 0)
        self.processed = self.config.get("processed", 0)
        self.debug = self.config.get("debug", "false")

    def save(self, result: RunResult = None):
        if result is not None:
            self.startTime = result.start_time
            self.endTime = result.end_time
            self.processed = result.iteration
        self.config["pollInterval"] = self.pollInterval
        self.config["pollLimit"] = self.pollLimit
        self.config["inputType"] = self.inputType
        self.config["outputType"] = self.outputType
        self.config["processorType"] = self.processorType
        self.config["startTime"] = self.startTime
        self.config["endTime"] = self.endTime
        self.config["processed"] = self.processed
        self.config["debug"] = self.debug
        util.save_properties(self.configFile, self.config)

    def get_name(self):
        return self.name

    def get(self, key, default=None):
        if default is not None and not key in self.config:
            self.config[key] = default
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value

class AppCtx:
    def __init__(self, app_name="app", config=Config()):
        self.name = app_name
        self.config = config

    def get_config(self)->Config:
        return self.config

    def get_name(self):
        return self.name

