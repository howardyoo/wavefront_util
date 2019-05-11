#!/bin/bash
OUTDIR="./queryout"
# search string - dashboard ids starting with this will be export imported
QUERY_FILE=""
# target endpoint
TARGET_PROXY=""
# token
TARGET_PORT=""
# start time (epoch seconds)
START_TIME="1470101400"
# end time (epoch seconds)
END_TIME="1470103860"

# check the arguments
if [ $# -ne 3 ]; then
	echo "Usage: $0 <queryfile> <proxyhost> <proxyport>"
	echo "queryfile: name of the file which contains lines of wf queries"
	echo "proxyhost: hostname (e.g. localhost)"
	echo "proxyport: Port number (e.g. 2878)"
	exit 1
fi

QUERY_FILE=$1
TARGET_PROXY=$2
TARGET_PORT=$3

echo "Starting Wavefront query run process..."

if [ ! -d "$OUTDIR" ]; then
	echo "directory $OUTDIR does not exist, creating a new one..."
	mkdir $OUTDIR
else
	echo "deleting contents of the directory $OUTDIR..."
	rm -rf $OUTDIR
	mkdir $OUTDIR
fi

SECONDS=0

echo "running wf command to run quries in $QUERY_FILE..."
while read line do
do
	if [ ${#line} -gt 0 ]; then
		# run wf command to run and fetch the queries
		echo "collecting from query: $line ..."
		sline=$( echo $line | sed "s/\"/\\\"/g" )
		wf query -P demo -f wavefront -s $START_TIME -e $END_TIME "$sline" >> $OUTDIR/wfquery.out
	fi
done < $QUERY_FILE

echo "Ingesting queries to wf proxy at $TARGET_PROXY on port $TARGET_PORT ..."
wf write file -E $TARGET_PROXY -p $TARGET_PORT -F wavefront $OUTDIR/wfquery.out 
echo "Ingestion finished."

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
