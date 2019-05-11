#!/bin/bash
OUTDIR="./queryout"

END_TIME=$( date +%s )

START_TIME=$((END_TIME - 21600))
HALF_TIME=$((END_TIME - 10800))

# 6 hours = 21600 seconds
# echo start time is $START_TIME
# echo end time is $END_TIME

# run the query using wf cli
wf query -f wavefront -P demo -s $START_TIME -e $END_TIME "ts(demo.alert.*)" > q.out

# sort the file
sort -k 3n q.out > sorted_q.out
rm q.out

