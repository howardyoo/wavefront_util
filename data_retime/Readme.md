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

