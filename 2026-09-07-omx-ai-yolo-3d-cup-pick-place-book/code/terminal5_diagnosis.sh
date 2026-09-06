#!/usr/bin/env bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 topic echo /joint_states --once
ros2 topic info /camera/color/image_raw
ros2 topic info /camera/depth/image_raw
echo 'TF continuous check: ros2 run tf2_ros tf2_echo base_link link5'
