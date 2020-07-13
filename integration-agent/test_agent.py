#!/usr/bin/python3

import test_classes as classes
import test_utility as util
import input_plugins.test_plugin_in as def_input_plugin
import output_plugins.test_plugin_out as def_output_plugin
import processors.test_pre_process as def_pre_processor

# collector collects data
# 1. init
# read the configuration file
# setup the collecting plugin
def init_plugins(context: classes.AppCtx):
    input_type = context.get_config().inputType
    output_type = context.get_config().outputType
    # get the classes
    input_plugin = util.get_plugin_class(input_type)
    output_plugin = util.get_plugin_class(output_type)
    # if none is found, initialize empty ones
    if input_plugin is None:
        input_plugin = def_input_plugin.InputPlugin
    if output_plugin is None:
        output_plugin = def_output_plugin.OutputPlugin
    return input_plugin(context), output_plugin(context)

def init_processor(context: classes.AppCtx):
    processor_type = context.get_config().processorType
    processor_plugin = util.get_plugin_class(processor_type)
    if processor_plugin is None:
        processor_plugin = def_pre_processor.PreProcessor
    return processor_plugin(context)

# 2. start collection loop
# check whether the last end time file exists
# if so, use that file to mark the start time
# if not, use the current time
# also, if the end time is too long ago, as configured, reset it.

# 3. collecting
# run the collection per required interval
# keep track of next interval

def main():
    print("---- main ----")
    app_ctx = classes.AppCtx("test_agent")
    _in, _out = init_plugins(app_ctx)
    _processor = init_processor(app_ctx)

    # setting and running input: result will be given
    _in.setup()
    result = _in.run()

    # you can pre-process the data here.
    _processor.setup()
    result = _processor.run(result)

    # setting and running output
    _out.setup()
    _out.run(result)

    # save configuration to file
    app_ctx.config.save(result)

print("---- test-agent start ----")
if __name__ == "__main__":
    main()

print("---- test-agent finished ----")