# ROS2 Integration Notes

## 권장 노드

```text
glove_driver_node
sync_node
dataset_recorder_node
retargeting_node
robot_command_node
```

## 예시 Topic

```text
/glove/fingers
/glove/imu
/glove/hand_pose
/vision/object_pose
/robot/joint_states
/robot/joint_command
```

초기 단계에서는 센서 장갑 데이터를 ROS2 `sensor_msgs` 또는 custom message로 publish하고,
이후 카메라/Depth/YOLO/로봇 데이터를 같은 timestamp 기준으로 동기화합니다.
