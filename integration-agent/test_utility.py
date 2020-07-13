#!/usr/bin/python3

import sys
from importlib import import_module

# read the properties file
def load_properties(filepath, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    try:
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    if value.isnumeric():
                        value = int(float(value))
                    props[key] = value
    except IOError:
        pass
    return props

def save_properties(filepath, props={}, sep='=', comment_char='#'):
    """
    Save the properties file in props to properties file path given
    intelligently scan and update the property only when the value has
    changed
    """
    new_props = []
    try:
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    if key in props.keys():
                        propval = props[key]
                        if type(propval) == str:
                            propval = propval.strip()
                        if propval != value:
                            l = key + sep + str(propval)
                        del props[key]
                new_props.append(l)
            # now append any remaining new property key and values
            for key, value in props.items():
                if type(value) != str:
                    value = str(value)
                new_props.append(key + sep + value)
    except IOError:
        # in case the file does not exist
        for key, value in props.items():
            if type(value) != str:
                value = str(value)
            new_props.append(key + sep + value)
    # now write the merged content to the property file
    with open(filepath, "wt") as f:
        for line in new_props:
            f.write(line + "\n")

def get_plugin_class(module_name):
    try:
        names = module_name.split(".")
        module = ""
        for x in names[:-1]:
            module = module + x + "."
        module = module[:-1]
        # print("module is", module)
        classname = names[-1]
        # print("class name is", classname)
        _module = import_module(module)
        _class = getattr(_module, classname)
    except ValueError:
        sys.stdout.write("get_plugin_class() Value Error, falling back to default...\n")
        return None
    except ImportError:
        sys.stdout.write("get_plugin_class() Error importing {0}, falling back to default...\n".format(module_name))
        return None
    return _class