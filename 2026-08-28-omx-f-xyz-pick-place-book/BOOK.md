# ROBOTIS OMX-F XYZ 좌표 제어와 자동 Pick & Place

## ROS 2 Jazzy + MoveIt + IK + TF + Cartesian XYZ Control

---

## 머리말

이번 실습의 목표는 ROBOTIS OMX-F 로봇팔을 단순히 관절 하나씩 조종하는 수준에서 한 단계 더 발전시켜, **로봇팔 끝단(End Effector)을 공간상의 XYZ 좌표를 기준으로 이동시키고, HOME / PICK / PLACE 위치를 저장하여 자동 Pick & Place까지 수행하는 시스템**을 만드는 것이다.

이번 실습에서 가장 중요한 변화는 다음과 같다.

기존 방식:

```text
joint1을 조금 움직인다
joint2를 조금 움직인다
joint3를 조금 움직인다
...
```

이번 방식:

```text
로봇팔 끝을 X, Y, Z의 목표 위치로 이동시킨다
        ↓
MoveIt이 IK를 계산한다
        ↓
joint1 ~ joint5의 목표값이 계산된다
        ↓
실제 OMX-F가 해당 위치로 이동한다
```

즉, 로봇팔을 **관절 중심 제어에서 공간 좌표 중심 제어로 발전시킨 실습**이다.

이 구조는 이후 Depth 카메라를 연결하여 카메라가 물체의 위치를 자동으로 찾아내고, 로봇이 그 위치를 집는 비전 기반 자동 Pick & Place 시스템으로 발전시키기 위한 핵심 기반이 된다.

---

# 1. 전체 시스템 개요

이번 실습에서는 총 4개의 터미널을 사용한다.

```text
Terminal 1 : 실제 OMX-F 하드웨어 연결
Terminal 2 : MoveIt / IK 계산
Terminal 3 : XYZ Cartesian Jog
Terminal 4 : HOME / PICK / PLACE 저장 + 자동 Pick & Place
```

전체 데이터 흐름은 다음과 같다.

```text
사람이 XYZ 목표를 만든다
        ↓
Terminal 3
        ↓
목표 Pose 생성
        ↓
Terminal 2 / MoveIt
        ↓
IK 계산
        ↓
joint1 ~ joint5 목표값
        ↓
Terminal 1 / ROS 2 Controller
        ↓
실제 OMX-F 모터
        ↓
End Effector 이동
        ↓
Terminal 4
        ↓
HOME / PICK / PLACE 저장
        ↓
자동 Pick & Place
```

---

# 2. 실습 환경

이번 실습에서 사용한 주요 환경은 다음과 같다.

- Ubuntu
- ROS 2 Jazzy
- ROBOTIS OMX-F
- MoveIt
- Python 3
- TF2
- ros2_control
- FollowJointTrajectory
- Gripper Action Controller

ROS 2 Workspace:

```text
~/Robotics/ros2_ws
```

프로젝트 폴더:

```text
~/omx_xyz_control
```

실제 OMX-F 포트:

```text
/dev/ttyACM1
```

---

# 3. Terminal 1 — 실제 OMX-F 하드웨어 연결

Terminal 1은 실제 OMX-F를 ROS 2 시스템에 연결하는 역할을 한다.

실행 명령:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

## 3.1 ROS 2 Jazzy 환경 불러오기

```bash
source /opt/ros/jazzy/setup.bash
```

이 명령은 현재 터미널에서 ROS 2 Jazzy 명령어를 사용할 수 있도록 환경을 설정한다.

쉽게 표현하면 다음과 같다.

> "이 터미널에서 지금부터 ROS 2를 사용하겠다."

---

## 3.2 OMX-F Workspace 불러오기

```bash
source ~/Robotics/ros2_ws/install/setup.bash
```

이 명령은 사용자가 빌드한 OpenManipulator 및 OMX-F 관련 ROS 2 패키지를 현재 터미널에서 사용할 수 있도록 한다.

---

## 3.3 실제 OMX-F 실행

```bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

이 명령은 실제 OMX-F 하드웨어와 ROS 2를 연결한다.

여기서:

```text
open_manipulator_bringup
```

은 OMX-F 하드웨어를 실행하기 위한 패키지다.

```text
omx_f.launch.py
```

는 OMX-F 전용 Launch 파일이다.

```text
port_name:=/dev/ttyACM1
```

은 실제 OMX-F가 연결된 USB 포트를 지정한다.

Terminal 1의 핵심 역할은 다음과 같다.

```text
ROS 2
  ↕
Controller Manager
  ↕
Dynamixel / OMX-F Hardware
```

정상 실행되면 대표적으로 다음 기능이 활성화된다.

```text
/joint_states
arm_controller
gripper_controller
joint_state_broadcaster
```

Terminal 1은 실험이 끝날 때까지 계속 실행해 둔다.

---

# 4. Terminal 2 — MoveIt과 역기구학 IK

Terminal 2는 MoveIt을 실행한다.

실행 명령:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

ros2 launch open_manipulator_moveit_config omx_f_moveit.launch.py
```

핵심 명령:

```bash
ros2 launch open_manipulator_moveit_config omx_f_moveit.launch.py
```

MoveIt은 로봇의 움직임을 계산하는 소프트웨어 프레임워크다.

이번 실습에서는 특히 **역기구학 IK(Inverse Kinematics)** 계산이 중요하다.

---

# 5. FK와 IK

로봇팔을 이해하기 위해 반드시 알아야 할 두 가지 개념이 있다.

## 5.1 FK — Forward Kinematics, 정기구학

FK는 각 관절의 각도를 알고 있을 때 로봇팔 끝의 위치를 계산하는 것이다.

```text
Joint Angles
     ↓
     FK
     ↓
X, Y, Z + Orientation
```

쉽게 말하면:

> "현재 관절들이 이런 상태인데, 그러면 로봇팔 끝은 어디에 있지?"

를 계산하는 방식이다.

---

## 5.2 IK — Inverse Kinematics, 역기구학

IK는 반대로 원하는 위치를 알고 있을 때 필요한 관절값을 계산한다.

```text
목표 X, Y, Z + Orientation
        ↓
        IK
        ↓
joint1 ~ joint5
```

쉽게 말하면:

> "로봇팔 끝을 이 XYZ 위치로 보내고 싶은데, 각 관절을 어떻게 움직여야 하지?"

를 계산하는 것이다.

가장 간단하게 기억하면:

```text
FK = 관절 → 좌표
IK = 좌표 → 관절
```

---

# 6. IK 계산은 왜 중요한가

예를 들어 다음 위치로 로봇팔 끝을 보내고 싶다고 하자.

```text
X = 0.180 m
Y = 0.020 m
Z = 0.150 m
```

사람이 직접 다음 값을 계산할 필요는 없다.

```text
joint1 = ?
joint2 = ?
joint3 = ?
joint4 = ?
joint5 = ?
```

MoveIt의 IK Solver가 OMX-F의 URDF와 관절 구조를 이용해서 필요한 관절값을 계산한다.

개념적인 처리 흐름:

```text
목표 XYZ
   +
Orientation
     ↓
MoveIt
     ↓
/compute_ik
     ↓
IK Solver
     ↓
joint1
joint2
joint3
joint4
joint5
```

실제 로봇공학에서는 삼각함수, 행렬, 좌표변환, 수치해석 등이 사용되지만, 사용자가 매번 모든 수학식을 직접 계산할 필요는 없다.

중요한 것은 **FK와 IK가 어떤 방향의 계산인지 이해하는 것**이다.

---

# 7. OMX-F 좌표계

이번 프로젝트에서 로봇 기준 좌표계는 다음 링크를 사용했다.

```text
link0
```

엔드 이펙터:

```text
end_effector_link
```

따라서 현재 로봇팔 끝 위치는 다음 TF 관계로 확인한다.

```text
link0 → end_effector_link
```

로봇 구조를 단순하게 표현하면 다음과 같다.

```text
link0
  ↓
joint1
  ↓
joint2
  ↓
joint3
  ↓
joint4
  ↓
joint5
  ↓
end_effector_link
```

---

# 8. Terminal 3 — XYZ Cartesian Jog

Terminal 3은 실제 OMX-F를 X, Y, Z 방향으로 조금씩 움직여 원하는 공간상의 위치를 만드는 역할을 한다.

실행 명령:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

cd ~/omx_xyz_control

python3 omx_cartesian_tf_control.py
```

프로그램 경로:

```text
~/omx_xyz_control/omx_cartesian_tf_control.py
```

사용 명령:

```text
x+    X 방향 +10 mm
x-    X 방향 -10 mm

y+    Y 방향 +10 mm
y-    Y 방향 -10 mm

z+    Z 방향 +10 mm
z-    Z 방향 -10 mm

p     현재 목표 좌표 확인
r     실제 TF 좌표 다시 읽기
q     종료
```

---

# 9. Terminal 3 내부 동작 원리

예를 들어 현재 X 좌표가:

```text
X = 0.180 m
```

이고 사용자가:

```text
x+
```

를 입력하면 목표는:

```text
X = 0.190 m
```

이 된다.

하지만 프로그램이 단순히 특정 모터 하나만 움직이는 것은 아니다.

실제로는 다음 과정이 일어난다.

```text
현재 TF 읽기
      ↓
현재 XYZ 확인
      ↓
X + 10 mm
      ↓
새 목표 Pose 생성
      ↓
/compute_ik
      ↓
MoveIt IK 계산
      ↓
joint1 ~ joint5 계산
      ↓
FollowJointTrajectory
      ↓
arm_controller
      ↓
실제 OMX-F 이동
```

따라서 Terminal 3은 쉽게 말하면:

> "로봇팔의 XYZ 위치를 만드는 조종기"

라고 볼 수 있다.

---

# 10. 목표 좌표와 실제 좌표

실제 로봇에서는 명령한 목표 좌표와 실제 도달 좌표가 완벽하게 같지 않을 수 있다.

실제 테스트 예:

```text
목표
X=0.186
Y=-0.029
Z=0.133

실제
X=0.186
Y=-0.029
Z=0.131
```

다른 테스트:

```text
목표
X=0.186
Y=-0.029
Z=0.121

실제
X=0.184
Y=-0.029
Z=0.119
```

몇 mm 정도의 오차가 발생할 수 있다.

따라서 실제 로봇에서는:

```text
목표 좌표
   ↓
이동
   ↓
실제 TF 재측정
```

과정이 중요하다.

---

# 11. Terminal 4 — HOME / PICK / PLACE 저장

Terminal 4는 위치 저장, 그리퍼 제어, 자동 Pick & Place를 담당한다.

실행:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

cd ~/omx_xyz_control

python3 omx_pick_place.py
```

프로그램:

```text
~/omx_xyz_control/omx_pick_place.py
```

메뉴:

```text
r = 현재 실제 XYZ 확인
s = 현재 위치 저장
l = 저장된 위치 확인

h = HOME 이동
k = PICK 이동
p = PLACE 이동

o = Gripper OPEN
c = Gripper CLOSE

a = AUTO PICK & PLACE
m = 메뉴
q = 종료
```

---

# 12. HOME / PICK / PLACE 저장 방법

## 12.1 HOME 저장

Terminal 3에서 안전한 HOME 위치를 만든다.

Terminal 4:

```text
s
1
```

현재 Pose를 HOME으로 저장한다.

---

## 12.2 PICK 저장

Terminal 3에서 물체를 잡을 위치까지 이동한다.

Terminal 4:

```text
s
2
```

현재 Pose를 PICK으로 저장한다.

---

## 12.3 PLACE 저장

Terminal 3에서 물체를 내려놓을 위치까지 이동한다.

Terminal 4:

```text
s
3
```

현재 Pose를 PLACE로 저장한다.

---

# 13. Pose는 XYZ만 저장하는 것이 아니다

실제 저장값은 단순한 X, Y, Z만이 아니다.

```text
Position
X
Y
Z
```

와 함께:

```text
Orientation
qx
qy
qz
qw
```

도 저장한다.

즉:

```text
Pose = Position + Orientation
```

이다.

물건을 위에서 잡을지, 옆에서 잡을지에 따라 그리퍼 방향이 중요하기 때문이다.

---

# 14. 저장 파일

HOME / PICK / PLACE는 다음 JSON 파일에 저장된다.

```text
~/omx_xyz_control/omx_pick_place_poses.json
```

따라서 프로그램을 종료했다가 다시 실행해도 이전에 저장한 위치를 불러올 수 있다.

---

# 15. 개별 위치 테스트

자동 동작을 바로 실행하지 않는다.

먼저 각각의 위치가 안전한지 확인한다.

Terminal 4:

```text
h
k
h
p
h
```

의미:

```text
HOME
 ↓
PICK
 ↓
HOME
 ↓
PLACE
 ↓
HOME
```

각 단계에서 바닥, 테이블, 주변 물체와의 충돌 여부를 반드시 확인한다.

---

# 16. 그리퍼 테스트

자동 실행 전에 그리퍼도 개별적으로 확인한다.

OPEN:

```text
o
```

CLOSE:

```text
c
```

실제 OMX-F의 그리퍼 방향, 개폐량, 물체 크기를 확인한다.

---

# 17. AUTO PICK & PLACE

모든 위치와 그리퍼가 안전하게 동작한다면 자동 실행한다.

Terminal 4:

```text
a
```

안전 확인 후 승인하면 자동 동작이 시작된다.

현재 자동 시퀀스:

```text
HOME
  ↓
GRIPPER OPEN
  ↓
PICK
  ↓
GRIPPER CLOSE
  ↓
HOME
  ↓
PLACE
  ↓
GRIPPER OPEN
  ↓
HOME
```

겉으로 보면 매우 단순한 움직임이지만, 중요한 것은 이 동작이 **저장된 공간상의 Pose와 IK 계산을 기반으로 실행된다는 점**이다.

---

# 18. Terminal 1 ~ 4 전체 관계

```text
┌─────────────────────────┐
│ Terminal 3              │
│ XYZ 목표 위치 생성       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Terminal 2              │
│ MoveIt / IK             │
│ XYZ → Joint Angles      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Terminal 1              │
│ ROS 2 Controller        │
│ 실제 OMX-F 구동          │
└────────────┬────────────┘
             ↓
       실제 로봇 이동
             ↓
┌─────────────────────────┐
│ Terminal 4              │
│ HOME/PICK/PLACE 저장     │
│ Gripper / Auto Sequence │
└─────────────────────────┘
```

한 문장씩 정리하면:

```text
Terminal 1 = 실제 로봇 하드웨어
Terminal 2 = 움직임 계산
Terminal 3 = XYZ 위치 만들기
Terminal 4 = 위치 기억 + 자동화
```

---

# 19. 이번 실습에서 반드시 이해해야 할 핵심

이번 실습의 핵심은 물체를 한 번 옮겼다는 것이 아니다.

가장 중요한 것은:

> OMX-F를 관절 중심 제어에서 XYZ 공간 좌표 중심 제어로 발전시켰다.

는 것이다.

기존:

```text
joint1
joint2
joint3
joint4
joint5
```

이번 실습:

```text
X
Y
Z
Orientation
```

을 목표로 준다.

그러면:

```text
목표 Pose
   ↓
IK
   ↓
Joint Angles
   ↓
Robot Motion
```

이 자동으로 계산된다.

---

# 20. Depth 카메라와 연결되는 이유

현재는 사람이 PICK 위치를 직접 정해서 저장한다.

하지만 Depth 카메라가 있다면 이 과정을 자동화할 수 있다.

예를 들어 컵을 인식한다고 하자.

RGB 영상:

```text
카메라 영상
   ↓
Object Detection
   ↓
Cup
   ↓
Cup Center Pixel
```

Depth:

```text
Cup Center Pixel
       ↓
Depth 값
       ↓
Camera 3D XYZ
```

---

# 21. 카메라 XYZ와 로봇 XYZ는 다르다

아주 중요한 부분이다.

Depth 카메라가 계산한 XYZ는:

```text
Camera Coordinate
```

다.

그러나 OMX-F가 사용하는 기준은:

```text
Robot link0 Coordinate
```

이다.

따라서 좌표변환이 필요하다.

```text
Camera XYZ
     ↓
Calibration
     ↓
TF Transformation
     ↓
Robot link0 XYZ
```

이 과정에서 Hand-Eye Calibration, TF, 변환행렬 등의 개념이 중요해진다.

---

# 22. 카메라 기반 자동 Pick 시스템

최종적으로 다음과 같은 구조로 발전한다.

```text
Depth Camera
      ↓
Cup Detection
      ↓
Center Pixel
      ↓
Depth
      ↓
Camera XYZ
      ↓
Coordinate Transform
      ↓
Robot link0 XYZ
      ↓
MoveIt
      ↓
IK
      ↓
joint1 ~ joint5
      ↓
OMX-F 이동
      ↓
Gripper Close
      ↓
Cup Pick
```

핵심 역할을 나누면:

```text
Camera = 물체가 어디 있는가?
IK     = 그곳까지 관절을 어떻게 움직일 것인가?
Robot  = 실제로 움직인다
```

---

# 23. 다음 단계 — Approach Pose

현재 시스템은 HOME에서 PICK으로 직접 이동한다.

실제 Pick & Place에서는 보다 안전한 접근 동작을 사용하는 것이 좋다.

개선된 구조:

```text
HOME
   ↓
PICK_APPROACH
   ↓
PICK
   ↓
GRIPPER CLOSE
   ↓
PICK_APPROACH
   ↓
PLACE_APPROACH
   ↓
PLACE
   ↓
GRIPPER OPEN
   ↓
PLACE_APPROACH
   ↓
HOME
```

이렇게 하면 물체 바로 위까지 먼저 이동한 뒤 수직으로 내려가서 잡고, 다시 수직으로 들어 올릴 수 있다.

충돌 위험도 줄일 수 있다.

---

# 24. 그 다음 단계 — 카메라가 PICK 좌표를 만든다

현재 방식:

```text
사람이 PICK 좌표를 지정
```

다음 방식:

```text
카메라가 PICK 좌표를 자동 생성
```

필요한 기술:

- Object Detection
- RGB + Depth
- Pixel Center
- Depth Measurement
- Camera Intrinsics
- Pixel → Camera XYZ
- Hand-Eye Calibration
- Camera → Robot Coordinate Transform
- TF2
- MoveIt
- IK
- Approach Pose
- Gripper Control

---

# 25. 컨베이어 시스템으로 확장

최종적으로는 다음과 같이 확장할 수 있다.

```text
Conveyor
    ↓
Depth Camera
    ↓
Object Detection
    ↓
Object XYZ
    ↓
Robot Coordinate
    ↓
MoveIt / IK
    ↓
OMX-F
    ↓
Pick
    ↓
Classification
    ↓
Place
```

물체가 항상 같은 장소에 있을 필요가 없다.

카메라가 새로운 위치를 측정하고 로봇이 새로운 위치로 이동한다.

이 단계부터는 단순한 반복 동작이 아니라 주변 환경을 인식해서 행동하는 로봇 시스템으로 발전하게 된다.

---

# 26. 실습 시 안전 원칙

실제 OMX-F를 사용할 때 반드시 다음을 확인한다.

1. Terminal 1의 하드웨어 연결이 정상인지 확인한다.
2. `/joint_states`가 정상적으로 들어오는지 확인한다.
3. HOME / PICK / PLACE 좌표가 서로 다른지 확인한다.
4. 자동 실행 전 개별 위치를 먼저 테스트한다.
5. 그리퍼 OPEN / CLOSE 방향을 먼저 확인한다.
6. 초기 테스트는 낮은 속도로 진행한다.
7. 바닥이나 테이블과의 충돌 가능성을 확인한다.
8. 필요하면 즉시 프로그램을 중단할 준비를 한다.
9. 로봇팔 끝을 바닥 가까이에 놓은 상태에서 무리하게 움직이지 않는다.
10. 처음부터 자동 실행하지 않고 단계별로 검증한다.

---

# 27. 실습 실행 순서 요약

## Terminal 1

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

## Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_moveit_config omx_f_moveit.launch.py
```

## Terminal 3

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd ~/omx_xyz_control
python3 omx_cartesian_tf_control.py
```

## Terminal 4

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
cd ~/omx_xyz_control
python3 omx_pick_place.py
```

실험 순서:

```text
1. Terminal 1 실행
2. Terminal 2 실행
3. Terminal 3 실행
4. Terminal 4 실행
5. Terminal 3으로 HOME 위치 생성
6. Terminal 4에서 HOME 저장
7. Terminal 3으로 PICK 위치 생성
8. Terminal 4에서 PICK 저장
9. Terminal 3으로 PLACE 위치 생성
10. Terminal 4에서 PLACE 저장
11. 저장 좌표 확인
12. HOME / PICK / PLACE 개별 테스트
13. Gripper OPEN / CLOSE 테스트
14. Auto Pick & Place 실행
```

---

# 28. 오늘 실습의 핵심 문장

오늘의 핵심을 한 문장으로 정리하면 다음과 같다.

> **오늘은 로봇에게 어디로 갈 것인가를 XYZ 좌표로 가르치는 방법을 구현했고, 다음 단계에서는 Depth 카메라가 그 XYZ 좌표를 스스로 찾아내도록 발전시킨다.**

그리고 조금 더 크게 보면:

> **카메라는 물체가 어디에 있는지를 찾고, IK는 그 위치까지 로봇팔을 어떻게 움직일지를 계산한다.**

이 두 기술이 연결되는 순간, 단순한 로봇팔 동작 테스트에서 **비전 기반 자율 Pick & Place 시스템**으로 발전하게 된다.

---

# 29. 결론

이번 프로젝트에서는 다음 단계를 실제로 연결했다.

```text
ROS 2 Hardware
      ↓
TF
      ↓
XYZ Cartesian Control
      ↓
MoveIt
      ↓
Inverse Kinematics
      ↓
Joint Trajectory
      ↓
OMX-F
      ↓
HOME / PICK / PLACE
      ↓
Auto Pick & Place
```

이 프로젝트는 완성점이 아니라 다음 단계로 넘어가기 위한 중요한 기반이다.

다음 목표는 다음과 같다.

```text
Depth Camera
   +
Object Detection
   +
3D XYZ
   +
Coordinate Transformation
   +
MoveIt IK
   +
OMX-F
   =
Vision-based Autonomous Pick & Place
```

이 과정을 단계적으로 구현하면, 향후 컨베이어 물류 시스템, 자동 분류 시스템, 휴머노이드 작업 학습 등으로 확장할 수 있다.
