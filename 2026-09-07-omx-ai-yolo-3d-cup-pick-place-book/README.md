# OMX AI Manipulator + YOLO 3D Cup Pick & Place

ROBOTIS OMX-F + Orbbec RGB-D + YOLO + ROS 2를 연결해 종이컵을 인식하고 3D 위치를 계산한 뒤 자동 Pick & Place로 확장하는 프로젝트입니다.

## Pipeline
`RGB-D → YOLO → (u,v) → Depth → Camera XYZ → Camera→Robot → OMX → Pick & Place`

## Terminal 1 — OMX-F
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

## Terminal 2 — Orbbec
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch ~/Robotics/ros2_ws/src/OrbbecSDK_ROS2/orbbec_camera/launch/gemini_330_series.launch.py
```

## Terminal 3 — YOLO 2D
```bash
source ~/Robotics/ros2_ws/install/setup.bash
source ~/yolo_venv/bin/activate
python ~/yolo_cup_detector.py
```

## Terminal 4 — YOLO + Depth 3D
```bash
source ~/Robotics/ros2_ws/install/setup.bash
source ~/yolo_venv/bin/activate
python ~/yolo_cup_3d.py
```

## Terminal 5 — Diagnosis
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 topic echo /joint_states --once
ros2 topic info /camera/color/image_raw
ros2 topic info /camera/depth/image_raw
ros2 run tf2_ros tf2_echo base_link link5
```

자세한 실험 기록과 원리는 `BOOK.md`를 참고하세요.
