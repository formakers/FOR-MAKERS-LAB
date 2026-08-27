#!/usr/bin/env bash
set -e
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f_follower_ai.launch.py port_name:=/dev/ttyACM1
