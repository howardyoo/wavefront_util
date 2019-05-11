#!/bin/bash

# the profile set in the .wavefront file
PROFILE=demo

wf source list -P $PROFILE -L 1000 > sources.txt
SRCS=$( cat sources.txt | wc -l )
echo $SRCS sources found.

# timer to calculate how much time it took
SECONDS=0

# iterate over the sources
START=0
echo "sourcetags" > sourcetags.txt
while read line
do
    echo "processing source: $line"
    echo "[$line]" >> sourcetags.txt
    # the last awk command removes any duplicate items from the lines
    wf query "hideBefore(30m, ts(azure.*, source=$line))" -f json -P $PROFILE -s -2h | jq .timeseries[].tags | awk '!seen[$0]++' >> sourcetags.txt
done < sources.txt

# run java program that will extract and produce @SourceTag string that can be fed into
# wavefront proxy
java -jar ./sourcetag.jar sourcetags.txt > sourcetag_data.txt

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."

# rm sourcetags.txt

