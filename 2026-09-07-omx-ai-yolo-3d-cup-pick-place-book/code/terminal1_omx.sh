#!/usr/bin/env bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
