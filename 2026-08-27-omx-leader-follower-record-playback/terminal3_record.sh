#!/usr/bin/env bash
set -e
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd "$(dirname "$0")"
python3 omx_follow_record_v2.py
