#!/bin/bash
# Flow Switch - free MVP launcher

cd "$(dirname "$0")"

line="================================================"
echo "$line"
echo "  Flow Switch - free MVP"
echo "$line"
echo ""

python3 manual_flow.py start

echo ""
read -p "Press Enter to close..."
