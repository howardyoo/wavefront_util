#!/usr/bin/env python
import random
import sys
import datetime
import time
import socket

# global variables definition
prefix = "demo.alert."
report_interval = 10
hourly_interval = 1
daily_interval = 1
minute_interval = 15
val_min = 0
val_max = 100
proxy_host = "127.0.0.1"
proxy_port = 2878

def correctVal(val):
  if val > val_max:
    return val_max
  elif val < val_min:
    return val_min
  else:
    return val

# class describing a system
# that has cpu, mem, diskio, networkio, etc
class System:
  def __init__(self, source, tags):
    self.source = source
    self.tags = tags
    self.metrics = {}
    self.prefix = prefix
    self.pattern = {} 
    self.scenario = Scenario(self)
    self.last_report = time.time()

  def getSource(self):
    return self.source

  def getScenario(self):
    return self.scenario

  def report(self):
    s = ""
    for k, v in self.metrics.items():
      if v is not None and v is not "":
        s += (self.prefix + k + " " + str(v) + " source=\"" + self.source + "\"")
        for t in self.tags:
          s += " " + t
        s += "\n"
    self.last_report = time.time()
    return s

  def setGauge(self, name, value, pattern=None):
    self.metrics[name] = value
    if pattern is not None:
      self.setPattern(name, pattern)

  def setPattern(self, metricName, pattern):
    self.pattern[metricName] = pattern

  def applyPattern(self):
    for k, v in self.pattern.items():
      v(self, k)

# Map which contains map of systems 
class SystemMap:
  def __init__(self):
    self.map = {}

  def addSystem(self, a_sys):
    self.map[a_sys.getSource()] = a_sys 

  def getSystem(self, source):
    return self.map[source]

  def run(self):
    for k, v in self.map.items():
      v.applyPattern()

  def report(self):
    s = ""
    for k, v in self.map.items():
      s += v.report()
    return s

# scenario class which will define what to do
# random selection choices:
# we need to be smart about this.
# 
class Scenario:
  def __init__(self, system):
    self.system = system;
    self.property = {}

  def setProperty(self, name, value):
    self.property[name] = value

  def getProperty(self, name):
    if name in self.property:
      return self.property[name]
    return None

# #############################
# function to mimic cpu pattern
def cpu_pattern(a_sys, metricName):
  s = a_sys.getScenario()
  delta = time.time() - a_sys.last_report     # in seconds

  # setup initial interval if not set
  if s.getProperty("cpu.interval.left") is None and s.getProperty("cpu.base.interval") is not None:
    s.setProperty("cpu.interval.left", s.getProperty("cpu.base.interval"))

  # setup current base if not set
  if s.getProperty("cpu.base.current") is None and s.getProperty("cpu.base") is not None:
    s.setProperty("cpu.base.current", s.getProperty("cpu.base"))

  # calculate and reduce interval left
  curr = s.getProperty("cpu.interval.left")
  if curr is not None:
    if curr < 0:
      # do something - in this case, we can adjust the cpu base value.
      # 1) do nothing and continue 2) raise the base value by raiseby(random) 3) go back to the base value
      choice = random.randint(1,3)
      if choice == 2:
        # raise the base value, between 0 and 100
        raiseby = random.randint(0, 100)
        s.setProperty("cpu.base.current", correctVal(s.getProperty("cpu.base") + raiseby))
      elif choice == 3:
        s.setProperty("cpu.base.current", s.getProperty("cpu.base"))

      # reset the interval to count down
      s.setProperty("cpu.interval.left", s.getProperty("cpu.base.interval"))
    else:
      s.setProperty("cpu.interval.left", curr - delta)

  # apply randomness if set
  if s.getProperty("cpu.random") == True:
    r = random.triangular(0, 1, 0.5)
    rv = r * s.getProperty("cpu.range")
    a_sys.metrics[metricName] = s.getProperty("cpu.base.current") + rv
  else:
    a_sys.metrics[metricName] = s.getProperty("cpu.base.current")

# #################################
# function to mimic storage pattern
def disk_pattern(a_sys, metricName):
  s = a_sys.getScenario()
  delta = time.time() - a_sys.last_report     # in seconds

  # setup initial interval if not set
  if s.getProperty("disk.interval.left") is None and s.getProperty("disk.base.interval") is not None:
    s.setProperty("disk.interval.left", s.getProperty("disk.base.interval"))

  # setup current base if not set
  if s.getProperty("disk.base.current") is None and s.getProperty("disk.base") is not None:
    s.setProperty("disk.base.current", s.getProperty("disk.base"))

  raiseby = 0

  # calculate and reduce interval left
  curr = s.getProperty("disk.interval.left")
  if curr is not None:
    if curr < 0:
      # do something - in this case, we can adjust the cpu base value.
      # 1) increase memory 2) decrease memory 3) go back to the base value
      choice = random.randint(1,5)
      if choice == 1:
        raiseby = random.randint(10, 60)
      else:
        s.setProperty("disk.base.current", s.getProperty("disk.base"))
      # reset the interval to count down
      s.setProperty("disk.interval.left", s.getProperty("disk.base.interval"))
    else:
      s.setProperty("disk.interval.left", curr - delta)

  # apply randomness if set
  if s.getProperty("disk.random") == True:
    r = random.triangular(0, 1, 0.5)
    rv = r * s.getProperty("disk.range")
    a_sys.metrics[metricName] = s.getProperty("disk.base.current") + rv + raiseby
  else:
    a_sys.metrics[metricName] = s.getProperty("disk.base.current") + raiseby

  # reset memory if the value goes over the top
  if a_sys.metrics[metricName] > val_max:
    a_sys.metrics[metricName] = s.getProperty("disk.base")

# ################################
# function to mimic memory pattern
def memory_pattern(a_sys, metricName):
  s = a_sys.getScenario()
  delta = time.time() - a_sys.last_report     # in seconds

  # setup initial interval if not set
  if s.getProperty("mem.interval.left") is None and s.getProperty("mem.base.interval") is not None:
    s.setProperty("mem.interval.left", s.getProperty("mem.base.interval"))

  # setup current base if not set
  if s.getProperty("mem.base.current") is None and s.getProperty("mem.base") is not None:
    s.setProperty("mem.base.current", s.getProperty("mem.base"))

  # calculate and reduce interval left
  curr = s.getProperty("mem.interval.left")
  if curr is not None:
    if curr < 0:
      # do something - in this case, we can adjust the cpu base value.
      # 1) increase memory 2) decrease memory 3) go back to the base value
      choice = random.randint(1,3)
      if choice == 1:
        raiseby = random.randint(0, 10)
        s.setProperty("mem.base.current", correctVal(s.getProperty("mem.base.current") + raiseby))
      elif choice == 2:
        # raise the base value, between 5 and 90
        lowerby = random.randint(0, 10)
        s.setProperty("mem.base.current", correctVal(s.getProperty("mem.base.current") - lowerby))
      elif choice == 3:
        s.setProperty("mem.base.current", s.getProperty("mem.base"))

      # reset the interval to count down
      s.setProperty("mem.interval.left", s.getProperty("mem.base.interval"))
    else:
      s.setProperty("mem.interval.left", curr - delta)

  # apply leakness if set
  if s.getProperty("mem.leak") == True:
    inc = random.randint(1,5)
    s.setProperty("mem.base.current", s.getProperty("mem.base.current") + inc)

  # apply randomness if set
  if s.getProperty("mem.random") == True:
    r = random.triangular(0, 1, 0.5)
    rv = r * s.getProperty("mem.range")
    a_sys.metrics[metricName] = s.getProperty("mem.base.current") + rv 
  else:
    # finally store the data  
    a_sys.metrics[metricName] = s.getProperty("mem.base.current")

  # reset memory if the value goes over the top
  if a_sys.metrics[metricName] > val_max:
    a_sys.metrics[metricName] = s.getProperty("mem.base")

# #################################
# function to mimic network pattern
def network_pattern(a_sys, metricName):
  s = a_sys.getScenario()
  delta = time.time() - a_sys.last_report     # in seconds

  # setup initial interval if not set
  if s.getProperty("net.interval.left") is None and s.getProperty("net.base.interval") is not None:
    s.setProperty("net.interval.left", s.getProperty("net.base.interval"))

  # setup current base if not set
  if s.getProperty("net.base.current") is None and s.getProperty("net.base") is not None:
    s.setProperty("net.base.current", s.getProperty("net.base"))

  # setup stop report (choke)
  if s.getProperty("net.stopreport.left") is None and s.getProperty("net.stopreport.interval") is not None:
    s.setProperty("net.stopreport.left", s.getProperty("net.stopreport.interval"))

  # calculate and reduce interval left
  curr = s.getProperty("net.interval.left")
  if curr is not None:
    if curr < 0:
      # do something - in this case, we can adjust the cpu base value.
      choice = random.randint(1,15)
      if choice == 1:
        raiseby = random.randint(0, 20)
        s.setProperty("net.base.current", correctVal(s.getProperty("net.base.current") + raiseby))
      elif choice >= 4 and choice <= 7:
        raiseby = random.randint(0, 8)
        s.setProperty("net.base.current", correctVal(s.getProperty("net.base.current") + raiseby))
      elif choice == 2:
        # sudden dip in the network
        lowerby = random.randint(40, 80)
        s.setProperty("net.base.current", correctVal(s.getProperty("net.base.current") - lowerby))
      elif choice == 3:
        s.setProperty("net.base.current", s.getProperty("net.base"))

      # reset the interval to count down
      s.setProperty("net.interval.left", s.getProperty("net.base.interval"))
    else:
      s.setProperty("net.interval.left", curr - delta)

  # stopreport loop - separate from normal loop.
  # honestly, I think this code is just too confusing. 
  # forgive me, I am not that skilled in python
  s_curr = s.getProperty("net.stopreport.left")
  if s_curr is not None:
    if s_curr < 0:
      if s.getProperty("net.stopreport.on") is not True:
        choice = random.randint(1,2)
        if choice == 1:
          # turn on the stop mode.
          s.setProperty("net.stopreport.on", True)
          s.setProperty("net.stopreport.count", 12)

      if s.getProperty("net.stopreport.count") < 0:
        s.setProperty("net.stopreport.on", False)
        s.setProperty("net.stopreport.left", s.getProperty("net.stopreport.interval"))
    else:
      s.setProperty("net.stopreport.left", s_curr - delta)
      if s.getProperty("net.stopreport.on") is True:
        s.setProperty("net.stopreport.count", s.getProperty("net.stopreport.count") - 1)

  # apply leakness if set
  if s.getProperty("net.leak") == True:
    inc = random.randint(1,4)
    s.setProperty("net.base.current", s.getProperty("net.base.current") + inc)

  # apply randomness if set
  if s.getProperty("net.random") == True:
    r = random.triangular(0, 1, 0.5)
    rv = r * s.getProperty("net.range")
    a_sys.metrics[metricName] = s.getProperty("net.base.current") + rv
  else:
    # finally store the data  
    a_sys.metrics[metricName] = s.getProperty("net.base.current")

  # apply noise
  if s.getProperty("net.noise") == True:
    noise = random.randint(1,20)
    if noise == 1:
      # make some noise - drop the network packet rate
      a_sys.metrics[metricName] = random.randint(1,10)

  # reset memory if the value goes over the top
  if a_sys.metrics[metricName] > val_max:
    a_sys.metrics[metricName] = s.getProperty("net.base")

  # if stop report is on, remove the value - so the metric will not survive (stop)
  if s.getProperty("net.stopreport.on") is True:
    a_sys.metrics[metricName] = None

# main function
if __name__ == "__main__":

  m = SystemMap()

  a_sys = System("app-01.host", {"env=demo"})
  a_sys.setGauge("cpu", 10.0, cpu_pattern)
  a_sys.setGauge("mem", 10.0, memory_pattern)
  a_sys.setGauge("diskio", 10.0, disk_pattern)
  a_sys.setGauge("net", 10.0, network_pattern)
  a_sys.getScenario().setProperty("cpu.base", 10)
  a_sys.getScenario().setProperty("cpu.random", True)
  a_sys.getScenario().setProperty("cpu.range", 10)
  a_sys.getScenario().setProperty("cpu.base.interval", 60)     # in seconds (1 min)
  a_sys.getScenario().setProperty("mem.base.interval", 180)    # in seconds
  a_sys.getScenario().setProperty("mem.base", 5)
  a_sys.getScenario().setProperty("disk.base", 0)
  a_sys.getScenario().setProperty("disk.base.interval", 10)
  a_sys.getScenario().setProperty("net.base", 16)
  a_sys.getScenario().setProperty("net.base.interval", 60)
  a_sys.getScenario().setProperty("net.noise", True)
  a_sys.getScenario().setProperty("net.random", True)
  a_sys.getScenario().setProperty("net.range", 1)
  m.addSystem(a_sys)

  b_sys = System("app-02.host", {"env=demo"})
  b_sys.setGauge("cpu", 10.0, cpu_pattern)      # the value given here actually doesn't matter
  b_sys.setGauge("mem", 10.0, memory_pattern)
  b_sys.setGauge("diskio", 10.0, disk_pattern)
  b_sys.getScenario().setProperty("cpu.base", 10)
  b_sys.getScenario().setProperty("cpu.random", True)
  b_sys.getScenario().setProperty("cpu.range", 10)
  b_sys.getScenario().setProperty("mem.base.interval", 300)    # in seconds
  b_sys.getScenario().setProperty("mem.base", 10)
  b_sys.getScenario().setProperty("mem.leak", True)    # memory leaking pattern - keeps increasing
  b_sys.getScenario().setProperty("disk.base", 0)
  b_sys.getScenario().setProperty("disk.base.interval", 20)
  m.addSystem(b_sys)

  c_sys = System("app-03.host", {"env=demo"})
  c_sys.setGauge("cpu", 10.0, cpu_pattern)      # the value given here actually doesn't matter
  c_sys.setGauge("mem", 10.0, memory_pattern)
  c_sys.setGauge("diskio", 10.0, disk_pattern)
  c_sys.setGauge("net", 10.0, network_pattern)
  c_sys.getScenario().setProperty("cpu.base", 12)
  c_sys.getScenario().setProperty("cpu.random", True)
  c_sys.getScenario().setProperty("cpu.range", 16)
  c_sys.getScenario().setProperty("mem.base.interval", 200)    # in seconds
  c_sys.getScenario().setProperty("mem.base", 12)
  c_sys.getScenario().setProperty("disk.base", 0)
  c_sys.getScenario().setProperty("disk.base.interval", 15)
  c_sys.getScenario().setProperty("net.base", 16)
  c_sys.getScenario().setProperty("net.random", True)
  c_sys.getScenario().setProperty("net.range", 1)
  c_sys.getScenario().setProperty("net.stopreport", True)        # points stop reporting
  c_sys.getScenario().setProperty("net.stopreport.interval", 60)        # points stop reporting
  m.addSystem(c_sys)

  d_sys = System("app-04.host", {"env=demo"})
  d_sys.setGauge("cpu", 10.0, cpu_pattern)      # the value given here actually doesn't matter
  d_sys.setGauge("mem", 10.0, memory_pattern)
  d_sys.setGauge("diskio", 10.0, disk_pattern)
  d_sys.getScenario().setProperty("cpu.base", 8)
  d_sys.getScenario().setProperty("cpu.random", True)
  d_sys.getScenario().setProperty("cpu.range", 10)
  d_sys.getScenario().setProperty("mem.base.interval", 120)    # in seconds
  d_sys.getScenario().setProperty("mem.base", 15)
  d_sys.getScenario().setProperty("disk.base", 0)
  m.addSystem(d_sys)

  #for x in range(0, 10):
  while(1):
    m.run()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((proxy_host, proxy_port))
    d = m.report()
    sys.stdout.write(d)
    sys.stdout.flush()
    s.send(d)
    s.close()
    time.sleep(report_interval)

