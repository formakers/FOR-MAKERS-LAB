# OMX AI Manipulator + Orbbec + YOLO 3D Cup Pick & Place

## 오늘의 목표
**AI가 보는 것과 로봇이 움직이는 것을 연결한다.**

종이컵 → Orbbec RGB-D → YOLO 2D 검출 → Depth → Camera XYZ → Camera→OMX 좌표변환 → OMX Pick & Place

## 1. OMX-F 로봇팔
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py \
  port_name:=/dev/ttyACM1
```
`joint1~joint5`, `gripper_joint_1` 상태를 ROS 2에서 읽고 제어한다.
```bash
ros2 topic echo /joint_states --once
```

## 2. Orbbec RGB-D 카메라
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch \
~/Robotics/ros2_ws/src/OrbbecSDK_ROS2/orbbec_camera/launch/gemini_330_series.launch.py
```
주요 토픽:
- `/camera/color/image_raw`
- `/camera/depth/image_raw`
- `/camera/color/camera_info`
- `/camera/depth/camera_info`
- `/camera/depth/points`

실험 확인값: Depth `16UC1`, little-endian. CameraInfo 1280×720.
Intrinsics: `fx≈605.864, fy≈605.997, cx≈639.539, cy≈354.387`.

## 3. YOLO 2D Cup Detection
```bash
source ~/Robotics/ros2_ws/install/setup.bash
source ~/yolo_venv/bin/activate
python ~/yolo_cup_detector.py
```
실험 환경: OpenCV 5.0.0, Ultralytics 8.4.132, `yolov8n.pt`.

RGB 영상 → YOLO → CUP Bounding Box → 중심 픽셀 `(u,v)`.
종이컵은 카메라를 비스듬히 두어 윗면과 옆면이 함께 보이게 했을 때 인식이 개선됐다.

## 4. Depth 3D 좌표
```bash
source ~/Robotics/ros2_ws/install/setup.bash
source ~/yolo_venv/bin/activate
python ~/yolo_cup_3d.py
```
계산:
```text
X = (u-cx) * Z / fx
Y = (v-cy) * Z / fy
Z = Depth
```
즉 `(u,v) + Depth + CameraInfo → Camera XYZ`.

## 5. 시스템 상태 / TF 진단
```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 topic list | grep -E '^/tf$|^/tf_static$|robot_description|joint_states'
ros2 topic echo /joint_states --once
ros2 topic info /camera/color/image_raw
ros2 topic info /camera/depth/image_raw
ros2 run tf2_ros tf2_echo base_link link5
```
오늘 `/joint_states`, `/robot_description`, `/tf`, `/tf_static` 토픽은 확인했다.
단, `/joint_states` header에 `base_link`가 있다고 해서 실제 TF tree에 해당 frame이 존재한다고 단정할 수 없다. `tf2_echo`에서 frame을 찾지 못한 문제는 다음 단계에서 `robot_state_publisher`, URDF 및 실제 TF tree를 계속 진단한다.

## Camera XYZ → OMX base_link XYZ
```text
P_robot = R × P_camera + T
```
`R`은 카메라와 로봇 좌표축의 회전 차이, `T`는 두 원점의 위치 차이다.

```text
camera_color_optical_frame
        ↓ Camera XYZ
      [R, T]
        ↓
     base_link
        ↓
 link1→link2→link3→link4→link5→gripper
```

## 전체 데이터 흐름
```text
종이컵
  ↓
Orbbec RGB-D
  ├─ RGB → YOLO → CUP → (u,v) ─┐
  └─ Depth Z ──────────────────┤
                               ↓
                         CameraInfo
                               ↓
                          Camera XYZ
                               ↓
                    Camera→Robot 변환
                               ↓
                         base_link XYZ
                               ↓
                         OMX Robot Arm
                               ↓
                     Approach→Pick→Place
```

## 오늘 사용한 주요 진단
```bash
ros2 topic hz /camera/color/image_raw
ros2 topic echo /camera/depth/image_raw --once --field encoding
ros2 topic echo /camera/depth/image_raw --once --field is_bigendian
ros2 topic echo /camera/color/camera_info --once
ros2 topic echo /camera/depth/camera_info --once
ros2 param get /camera/camera depth_registration
ros2 param get /camera/camera align_target_stream
ros2 param get /camera/camera align_mode
```
실험 중 확인: `depth_registration=False`, `align_target_stream=COLOR`, `align_mode=SW`.

## 문제 해결 기록
- RGB publisher가 0이면 YOLO 화면이 기다림 → 카메라 launch 후 `Publisher count: 1` 확인.
- `python` 명령 없음 → `source ~/yolo_venv/bin/activate`.
- 종이컵 검출 약함 → 카메라 사선 배치로 개선.
- TF의 `base_link` 미검출 → 실제 TF tree를 별도로 진단.

## 의미
카메라는 눈, YOLO는 시각 인식, Depth는 공간 감각, ROS 2/TF는 정보와 좌표를 연결하고, OMX는 실제 행동하는 팔과 손이다.

## 다음 단계
1. OMX TF tree 정상화
2. Camera↔OMX extrinsic calibration
3. Camera XYZ→`base_link` XYZ 검증
4. Pre-grasp/IK/trajectory
5. Gripper Pick
6. Place
7. 컵 위치를 바꾸며 자동 반복 테스트
