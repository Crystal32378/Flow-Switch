#!/bin/bash
# Flow Switch - free MVP setup

cd "$(dirname "$0")"

line="================================================"
echo "$line"
echo "  Flow Switch - free MVP setup"
echo "$line"
echo ""
echo "  This version does not need Premium or Web API authorization."
echo "  Paste four playlist or album links, then use 5_manual_start.command to pick a mode."
echo ""

python3 manual_flow.py setup

echo ""
read -p "Press Enter to close..."
