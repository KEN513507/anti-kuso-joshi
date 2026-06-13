#!/bin/bash
pkill -9 screen 2>/dev/null
sudo fuser -k /dev/ttyACM0 2>/dev/null
sleep 1
picocom -b 115200 /dev/ttyACM0
