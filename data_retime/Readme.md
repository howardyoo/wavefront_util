# Data Re-time utility #
This utility converts the timestamp of the Wavefront data file (which is lines of WF data format) 
that converts the past time to align with the current time for better demo-ing of Wavefront.

The utility scans the file, calculates the mid-point of time of start and end timestamp, and
positions itself on the mid-point to the current timestamp, thereby effectively back-filling any data
that is older than the mid-point.

As for the other remaining half, it then goes into interval loading them in real time per each second, 
grabbing set of data that constitute to the current timestamp.

The utility assumes that the data file's timestamps are all sorted in Ascending order.
There is a script that generates the query and sorts the data as well.

There are two files in this utility that may be helpful
1. get6hour.sh
 - this is a bash script that uses wf cli to run a query which is included in the script and 
   sort the resulting WF data into timestamp-asc. In many cases, you would need to open this file
   and edit the settings for your usage.
2. retime.py
 - retime.py --help will display the help information, but in general, this python script requires inputfile to read
   and run.
 - there is also a -d or --debug mode where, when entered, will make the script going into debug mode which will
   not send the data to the wavefront proxy, but will send the output to the standard output.
 - You can also set the proxy host and port by setting -t and -p with appropriate values. The default settings are
   localhost and 2878.

