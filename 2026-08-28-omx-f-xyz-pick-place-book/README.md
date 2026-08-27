# 2026-08-28 ROBOTIS OMX-F XYZ Pick & Place

ROS 2 Jazzy + MoveIt + TF + IK를 이용하여 ROBOTIS OMX-F를 XYZ 좌표 기반으로 제어하고, HOME / PICK / PLACE 위치를 저장하여 자동 Pick & Place를 실행한 실습 프로젝트입니다.

## 핵심 흐름

```text
XYZ Target
   ↓
MoveIt
   ↓
Inverse Kinematics
   ↓
Joint Angles
   ↓
OMX-F
   ↓
HOME / PICK / PLACE
   ↓
Auto Pick & Place
```

## 4개 터미널

### Terminal 1 — Hardware

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

### Terminal 2 — MoveIt / IK

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_moveit_config omx_f_moveit.launch.py
```

### Terminal 3 — XYZ Cartesian Control

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd ~/omx_xyz_control
python3 omx_cartesian_tf_control.py
```

### Terminal 4 — Pose Memory / Auto Pick & Place

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd ~/omx_xyz_control
python3 omx_pick_place.py
```

## 상세 문서

전체 학습 내용은 [BOOK.md](BOOK.md)를 참고하세요.

## 다음 단계

```text
Depth Camera
→ Object Detection
→ Pixel + Depth
→ Camera XYZ
→ Robot XYZ
→ MoveIt IK
→ OMX-F Pick
```

목표는 카메라가 직접 물체의 PICK 좌표를 생성하는 비전 기반 자동 Pick & Place입니다.
