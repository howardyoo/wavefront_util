#!/bin/bash
OUTDIR="./queryout"
DEBUG=0

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

if [ "$DEBUG" -ne 0 ]; then
echo "Starting Wavefront query run process..."
fi

if [ ! -d "$OUTDIR" ]; then
	echo "directory $OUTDIR does not exist, creating a new one..."
	mkdir $OUTDIR
else
	echo "deleting contents of the directory $OUTDIR..."
	rm -rf $OUTDIR
	mkdir $OUTDIR
fi

SECONDS=0

echo "running wf command to run quries in $QUERY_FILE between time of $START_TIME and $END_TIME ..."
while read line
do
	if [ ${#line} -gt 0 ]; then
		# run wf command to run and fetch the queries
		echo "collecting from query: $line ..."
		sline=$( echo $line | sed "s/\"/\\\"/g" )
		wf query -f wavefront -s $START_TIME -e $END_TIME $WF_QUERY_ARGS "$sline" >> $OUTDIR/wfquery.out
		echo "output written to ${OUTDIR}/wfquery.out with $( wc -l < $OUTDIR/wfquery.out ) points total."
	fi
done < $QUERY_FILE

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
