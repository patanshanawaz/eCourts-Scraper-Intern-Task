#!/usr/bin/env bash
# Simple runner to give you time to start recording.
# Usage: ./run_record.sh <state> <district> <complex> <court> [--case <query>] [--causelist]

if [ $# -lt 4 ]; then
  echo "Usage: $0 <state> <district> <complex> <court> [--case <query>] [--causelist]"
  exit 1
fi

STATE=$1
DIST=$2
COMP=$3
COURT=$4
shift 4

# Give you 6 seconds to start screen recording
echo "Start your screen recorder (QuickTime/OBS). Script will begin in 6 seconds..."
sleep 6

source .venv/bin/activate

python main.py --state "$STATE" --district "$DIST" --complex "$COMP" --court "$COURT" "$@"
