#!/bin/bash
EXPDIR="./export"
# search string - dashboard ids starting with this will be export imported
DASH_SEARCH=""
# target endpoint
TARGET_ENDPOINT=""
# token
TARGET_TOKEN=""

# check the arguments
if [ $# -ne 3 ]; then
	echo "Usage: $0 <name> <endpoint> <token>"
	echo "name: name of the dashboard (starts with)"
	echo "endpoint: endpoint of the target (e.g. longboard.wavefront.com)"
	echo "token: API token"
	exit 1
fi

DASH_SEARCH=$1
TARGET_ENDPOINT=$2
TARGET_TOKEN=$3

echo "Starting Wavefront dashboard import process..."

if [ ! -d "$EXPDIR" ]; then
	echo "directory $EXPDIR does not exist, creating a new one..."
	mkdir $EXPDIR
else
	echo "deleting contents of the directory $EXPDIR..."
	rm -rf $EXPDIR
	mkdir $EXPDIR
fi

SECONDS=0

echo "running wf command to export dashboards with search string $DASH_SEARCH..."
wf dashboard search name~$DASH_SEARCH | awk '{print $1}' | awk -v ODIR=$EXPDIR '{system("wf dashboard describe -f json " $1 " > " ODIR "/" $1 ".json")}'

FILES=`ls $EXPDIR/*.json`
COUNT=$(( ${#FILES[@]} + 1 ))

echo "found $COUNT dashboards to import..."

echo "Importing exported dashboards..."
START=1
for afile in $FILES
do
	echo "[$START/$COUNT] Importing $afile to $TARGET_ENDPOINT..."
	wf dashboard import -E $TARGET_ENDPOINT -t $TARGET_TOKEN -f json $afile
	START=$(( $START + 1 )) 
done

echo "Export Import finished, exported $COUNT dashboards."
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
