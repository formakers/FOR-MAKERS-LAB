#!/usr/bin/env bash
set -e
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd "$(dirname "$0")"
python3 omx_playback_smooth_v2.py
