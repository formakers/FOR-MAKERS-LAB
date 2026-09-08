# ROBOTIS OMX AI 매니퓰레이터 컵 자동 집기 실습서
## ROS 2 Jazzy + Orbbec Depth Camera + YOLO + MoveIt

---

## 1. 프로젝트 개요

이 실습서는 오늘 실제로 테스트한 **ROBOTIS OMX AI Manipulator 컵 자동 집기 시스템**의 터미널 실행 흐름을 정리한 책입니다.

전체 시스템은 다음 4개의 터미널로 구성합니다.

```text
터미널 1 : OMX-F Bringup
터미널 2 : Depth Camera + MoveIt
터미널 3 : YOLO + Depth 컵 3D 좌표 계산
터미널 4 : 최종 자동 컵 집기
```

최종 동작 순서는 다음과 같습니다.

```text
HOME
  ↓
GRIPPER OPEN
  ↓
CUP DETECTION
  ↓
APPROACH
  ↓
DESCEND 20 mm
  ↓
GRIPPER CLOSE
  ↓
LIFT 40 mm
  ↓
HOME
```

---

# 2. 터미널 1 — OMX-F Bringup

## 역할

터미널 1은 실제 OMX-F 로봇 하드웨어와 ROS 2를 연결합니다.

주요 역할은 다음과 같습니다.

- OMX-F 모터 연결
- `/joint_states` 발행
- `arm_controller` 활성화
- `gripper_controller` 활성화
- 로봇 TF 생성
- 실제 로봇 제어 준비

## 실행 명령

```bash
cd ~/Robotics/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py \
  port_name:=/dev/ttyACM2
```

> 현재 테스트에서 정상적으로 사용한 포트는 `/dev/ttyACM2`입니다.  
> USB를 다시 연결하거나 전원을 재인가하면 포트 번호가 바뀔 수 있습니다.

## 포트 확인

```bash
ls -l /dev/ttyACM*
```

## Controller 확인

새 터미널에서:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

ros2 control list_controllers
```

정상 상태 예:

```text
joint_state_broadcaster   active
arm_controller            active
gripper_controller        active
```

## Joint State 확인

```bash
ros2 topic hz /joint_states
```

실제 테스트에서는 약 100 Hz로 들어왔습니다.

```text
average rate: 99.9...
```

현재 자세 확인:

```bash
ros2 topic echo /joint_states --once
```

실제 Bringup 직후 확인한 HOME 값:

```text
joint1 =  0.000000
joint2 = -1.572330
joint3 = +1.569262
joint4 = +1.540117
joint5 = -0.001534

gripper_joint_1 ≈ +0.165670
```

이 값은 최종 자동화 프로그램의 HOME 자세 기준으로 사용했습니다.

---

# 3. 터미널 2 — Depth Camera + MoveIt

## 역할

터미널 2는 두 가지 핵심 기능을 담당합니다.

```text
Orbbec Gemini 335L
        +
MoveIt
```

카메라는 RGB와 Depth 데이터를 발행하고, MoveIt은 OMX-F가 목표 위치까지 갈 수 있도록 모션을 계획합니다.

---

## 3-1. 카메라 실행

먼저 환경을 불러옵니다.

```bash
cd ~/Robotics/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

현재 설치된 Orbbec launch 파일 확인:

```bash
find $(ros2 pkg prefix orbbec_camera)/share/orbbec_camera \
  -maxdepth 3 \
  -type f | grep launch
```

또는 소스 워크스페이스에서:

```bash
find ~/Robotics/ros2_ws/src \
  -type f \
  \( -name "*.launch.py" -o -name "*.launch.xml" \) \
  | grep -Ei "orbbec|gemini|camera"
```

실제 설치본에 맞는 Gemini 335L/330 계열 launch 파일을 찾아 실행합니다.

예시:

```bash
ros2 launch orbbec_camera <실제_설치된_launch_파일명>
```

## 카메라 Topic 확인

```bash
ros2 topic list | grep camera
```

필요한 핵심 Topic:

```text
/camera/color/camera_info
/camera/color/image_raw
/camera/depth/image_raw
```

Publisher 확인:

```bash
ros2 topic info /camera/color/image_raw
ros2 topic info /camera/depth/image_raw
```

정상 상태:

```text
Publisher count: 1
```

Frame rate 확인:

```bash
ros2 topic hz /camera/color/image_raw
```

```bash
ros2 topic hz /camera/depth/image_raw
```

---

## 3-2. MoveIt 실행

```bash
cd ~/Robotics/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch open_manipulator_moveit_config omx_f_moveit.launch.py
```

MoveIt은 실행한 터미널을 종료하지 않고 계속 유지합니다.

## MoveIt Node 확인

```bash
ros2 node list | grep move_group
```

정상:

```text
/move_group
```

## Move Action 확인

```bash
ros2 action info /move_action
```

정상:

```text
Action servers: 1
    /move_group
```

## IK 서비스 확인

```bash
ros2 service info /compute_ik
```

정상:

```text
Services count: 1
```

---

# 4. 터미널 3 — YOLO + Depth 컵 3D 좌표 계산

## 역할

터미널 3은 카메라에서 받은 RGB/Depth 데이터를 이용하여 컵의 3D 위치를 계산합니다.

흐름:

```text
RGB Image
   ↓
YOLO Cup Detection
   ↓
Cup Center Pixel
   ↓
Depth 값
   ↓
Camera XYZ
   ↓
/cup/camera_xyz
```

## 실행 명령

```bash
cd ~/Robotics/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

source ~/yolo_venv/bin/activate

python3 cup_3d_detector.py
```

정상 시작 로그:

```text
CUP 3D DETECTOR START

/camera/color/image_raw
/camera/depth/image_raw
/cup/camera_xyz
```

컵이 검출되면:

```text
CUP DETECTED

Confidence : ...
Pixel      : u=..., v=...
Depth      : 0.466 m

Camera XYZ
X = ...
Y = ...
Z = ...

Published -> /cup/camera_xyz
```

## Cup XYZ 직접 확인

```bash
ros2 topic echo /cup/camera_xyz --once
```

실제 테스트 대표값:

```text
x: -0.028873
y: +0.005854
z: +0.466
```

---

# 5. Camera XYZ → OMX Robot XYZ 변환

실제 테스트를 통해 OMX 좌표축을 확인했습니다.

```text
+X = 로봇 전방 / 카메라 방향
 Y = 좌우
+Z = 위쪽
```

현재 사용한 보정식:

```text
Robot X = Camera Z - 0.289000
Robot Y = Camera X + 0.005873
Robot Z = -Camera Y + 0.232854
```

대표 기준점:

```text
Camera XYZ
X = -0.028873
Y = +0.005854
Z = +0.466

↓

Robot XYZ
X ≈ +0.177
Y ≈ -0.023
Z ≈ +0.227
```

이 위치가 컵 위 APPROACH 기준점으로 사용되었습니다.

---

# 6. TF 확인 명령

## link0 → link5

```bash
ros2 run tf2_ros tf2_echo link0 link5
```

## link5 → end_effector_link

```bash
ros2 run tf2_ros tf2_echo link5 end_effector_link
```

## link0 → end_effector_link

```bash
ros2 run tf2_ros tf2_echo link0 end_effector_link
```

정상이라면:

```text
Translation: [x, y, z]
Rotation: ...
```

이 계속 출력됩니다.

## Static TF 확인

```bash
ros2 topic echo /tf_static --once | \
grep -E "frame_id|child_frame_id"
```

정상 관계 중 하나:

```text
frame_id: link5
child_frame_id: end_effector_link
```

---

# 7. 실제 축 방향 테스트

## Z +20 mm 테스트

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

python3 z_plus_20mm_test.py
```

실제 실행:

```bash
python3 z_plus_20mm_test.py --execute
```

확인 결과:

```text
+Z = 위쪽
```

---

## X +20 mm 테스트

```bash
python3 x_plus_20mm_test.py
```

실제 실행:

```bash
python3 x_plus_20mm_test.py --execute
```

확인 결과:

```text
+X = 로봇 전방 / 카메라 방향
```

---

## Y +20 mm 테스트

```bash
python3 y_plus_20mm_test.py
```

실제 실행:

```bash
python3 y_plus_20mm_test.py --execute
```

확인 결과:

```text
Y = 좌우 방향
```

---

# 8. MoveIt Z +20 mm Planning 테스트

기존의 단일 목표 JointTrajectory 방식보다 MoveIt이 다중 trajectory point를 생성하도록 변경했습니다.

DRY-RUN:

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

python3 movegroup_z_plus_20mm_test.py
```

성공 로그:

```text
Error code = 1
Trajectory points = 9

DRY RUN SUCCESS
```

실제 실행:

```bash
python3 movegroup_z_plus_20mm_test.py --execute
```

---

# 9. Cup APPROACH Planning 테스트

컵 위 접근 위치:

```text
X = +0.1780 m
Y = -0.0246 m
Z = +0.2270 m
```

Planning-only 실행:

```bash
python3 cup_approach_plan_test.py
```

실제 성공 결과:

```text
Error code = 1
Trajectory points = 33

PLAN SUCCESS
```

---

# 10. Cup APPROACH 실제 실행

DRY-RUN:

```bash
python3 cup_approach_execute_test.py
```

실제 실행:

```bash
python3 cup_approach_execute_test.py --execute
```

목표:

```text
X = +0.1780
Y = -0.0246
Z = +0.2270
```

---

# 11. DESCEND -20 mm

현재 APPROACH 위치에서 Z축으로만 20 mm 하강합니다.

DRY-RUN:

```bash
python3 cup_descend_20mm_test.py
```

실제 실행:

```bash
python3 cup_descend_20mm_test.py --execute
```

예상:

```text
APPROACH Z ≈ 0.227
        ↓
DESCEND Z ≈ 0.207
```

---

# 12. Gripper Slow Close 테스트

팔은 움직이지 않고 그리퍼만 테스트합니다.

DRY-RUN:

```bash
python3 gripper_close_slow_test.py
```

실제 실행:

```bash
python3 gripper_close_slow_test.py --execute
```

단계별 Close:

```text
0.150
0.135
0.120
0.105
0.090
0.075
0.060
0.045
0.030
0.015
0.000 rad
```

컵이 잡혀 `stalled=True`가 감지되면 추가 Close를 중단하도록 구성했습니다.

---

# 13. LIFT +40 mm

컵을 잡은 상태에서 Z축으로 40 mm 들어 올립니다.

DRY-RUN:

```bash
python3 cup_lift_40mm_test.py
```

실제 실행:

```bash
python3 cup_lift_40mm_test.py --execute
```

예:

```text
현재 Z ≈ 0.193
      ↓
목표 Z ≈ 0.233
```

---

# 14. 터미널 4 — 최종 자동 컵 집기

최종 자동화 프로그램:

```text
omx_auto_cup_pick_final.py
```

## DRY-RUN

```bash
cd ~/Robotics/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

python3 omx_auto_cup_pick_final.py
```

정상 흐름:

```text
CUP APPROACH TARGET

X ≈ +0.178
Y ≈ -0.024
Z ≈ +0.227

SIMULATED DESCEND
Z ≈ +0.207

SIMULATED LIFT
Z ≈ +0.247

DRY RUN SUCCESS
```

## 실제 자동 실행

```bash
python3 omx_auto_cup_pick_final.py \
  --execute \
  --confirm PICK \
  --descend-mm 20 \
  --lift-mm 40
```

최종 순서:

```text
1. HOME
2. GRIPPER OPEN
3. CUP DETECTION
4. APPROACH
5. DESCEND 20 mm
6. GRIPPER CLOSE
7. LIFT 40 mm
8. HOME
```

MoveIt 설정:

```text
Velocity     : 10%
Acceleration : 10%
```

---

# 15. 최종 4개 터미널 실행 요약

## TERMINAL 1

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py \
  port_name:=/dev/ttyACM2
```

## TERMINAL 2

카메라 실행 후 MoveIt:

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch orbbec_camera <실제_설치된_Gemini_launch_파일>
```

별도 탭/터미널에서 MoveIt:

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch open_manipulator_moveit_config \
  omx_f_moveit.launch.py
```

## TERMINAL 3

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
source ~/yolo_venv/bin/activate

python3 cup_3d_detector.py
```

## TERMINAL 4

DRY-RUN:

```bash
cd ~/Robotics/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

python3 omx_auto_cup_pick_final.py
```

실제 실행:

```bash
python3 omx_auto_cup_pick_final.py \
  --execute \
  --confirm PICK \
  --descend-mm 20 \
  --lift-mm 40
```

---

# 16. 실행 전 체크리스트

```text
[ ] OMX-F 전원 ON
[ ] /dev/ttyACM 포트 확인
[ ] /joint_states 약 100 Hz
[ ] arm_controller active
[ ] gripper_controller active
[ ] RGB Publisher count = 1
[ ] Depth Publisher count = 1
[ ] /move_action Action server = /move_group
[ ] /compute_ik Services count = 1
[ ] /cup/camera_xyz 발행
[ ] link0 → end_effector_link TF 정상
[ ] DRY-RUN 성공
```

---

# 17. 오늘 실습에서 확인된 핵심 포인트

처음에는 카메라 좌표와 로봇 좌표가 뒤섞이면서 로봇이 예상과 다른 방향으로 움직였습니다.

그래서 다음 과정을 실제 하드웨어에서 하나씩 검증했습니다.

```text
카메라 Depth 확인
↓
Camera XYZ 계산
↓
link0 기준 좌표 확인
↓
end_effector_link 기준점 확인
↓
X/Y/Z 실제 방향 확인
↓
MoveIt Planning
↓
APPROACH
↓
DESCEND
↓
GRIP
↓
LIFT
↓
HOME
```

가장 중요한 변화는 직접 한 점짜리 JointTrajectory 명령을 보내는 방식에서 벗어나, MoveIt이 여러 trajectory point를 계산해서 실행하도록 변경한 것입니다.

최종 시스템은 단순한 로봇팔 테스트가 아니라 다음 기술이 하나로 연결된 작은 AI 로봇 시스템입니다.

```text
Depth Camera
+ Computer Vision
+ YOLO
+ 3D Coordinate
+ ROS 2 Jazzy
+ MoveIt
+ ROBOTIS OMX
+ Python
```

---

## 최종 시스템

```text
Orbbec Gemini 335L
       ↓
RGB + Depth
       ↓
YOLO Cup Detection
       ↓
Camera XYZ
       ↓
OMX link0 XYZ
       ↓
MoveIt Motion Planning
       ↓
ROBOTIS OMX AI Manipulator
       ↓
APPROACH
       ↓
DESCEND
       ↓
GRIP
       ↓
LIFT
       ↓
HOME
```

---

**FOR MAKERS LAB**

AI와 로봇을 직접 만들고, 실행하고, 실패하고, 다시 수정하면서 배우는 메이커 프로젝트.
