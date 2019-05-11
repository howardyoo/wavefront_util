#!/bin/bash
OUTDIR="./queryout"

# check the arguments
if [ $# -lt 3 ]; then
	echo "Usage: $0 <start_time> <end_time> <query_file> [wf-query-args]"
	echo "start_time: start time in epoch seconds"
	echo "end_time: end time in epoch seconds"
	echo "query_file: name of the file which contains lines of wf queries"
	echo "wf-query-args: optional query arguments for wf cli"
	exit 1
fi

START_TIME=$1
END_TIME=$2
QUERY_FILE=$3
WF_QUERY_ARGS=$4

while read line do
do
	if [ ${#line} -gt 0 ]; then
		# run wf command to run and fetch the queries
		sline=$( echo $line | sed "s/\"/\\\"/g" )
		wf query -f wavefront -s $START_TIME -e $END_TIME $WF_QUERY_ARGS "$sline"
	fi
done < $QUERY_FILE

