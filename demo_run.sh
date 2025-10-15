#!/usr/bin/env bash
# demo_run.sh
# Automates the steps to demonstrate the project. This script assumes:
# - .venv is present and activated or available
# - You started recording before the pause finishes
# Usage: ./demo_run.sh <state> <district> <complex> <court> <example_cnr>

if [ $# -lt 5 ]; then
  echo "Usage: $0 <state> <district> <complex> <court> <example_cnr>"
  exit 1
fi

STATE=$1
DIST=$2
COMP=$3
COURT=$4
CNR=$5

echo "Demo will start in 8 seconds. Start your screen recorder now."
sleep 8

# Activate venv if exists
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

echo "1) Show repository files"
ls -l
sleep 2

echo "2) Run cause list download (visible browser). This may open Chrome." 
python main.py --state "$STATE" --district "$DIST" --complex "$COMP" --court "$COURT" --causelist --no-headless

echo "3) Run case search for example CNR: $CNR"
python main.py --state "$STATE" --district "$DIST" --complex "$COMP" --court "$COURT" --case "$CNR" --no-headless

echo "4) Show output files"
ls -l cause_list_* case_search_*

echo "Demo finished. Stop your recorder and save the file."
