#!/bin/bash
echo "Starting Bitcraft Market Backend..."
python main.py &

echo "Starting Bitcraft Market Frontend..."
python frontend.py
