# OMX-F 로봇팔 터미널 제어 실전 가이드

**부제:** ROS 2 Jazzy에서 OpenManipulator OMX-F를 처음부터 실행하고 Joint 1~5와 Gripper까지 제어하는 방법

---

## 1. 이 책의 목적

이 문서는 Ubuntu + ROS 2 Jazzy 환경에서 OpenManipulator OMX-F 로봇팔을 직접 실행하고,
각 관절을 하나씩 움직이며 로봇의 동작 구조를 이해하기 위한 실전 가이드입니다.

전체 구조는 매우 단순합니다.

- **터미널 1**: OMX-F 하드웨어와 ROS 2 컨트롤러를 실행하는 메인 터미널
- **터미널 2**: Joint 1~5와 Gripper에 실제 동작 명령을 보내는 제어 터미널

터미널 1은 로봇을 켜 두는 역할이고,
터미널 2는 로봇에게 “어디로 움직여라”라고 지시하는 역할입니다.

---

# 2. 현재 확인된 OMX-F 관절 구성

실제 `/joint_states`에서 확인한 관절 이름은 다음과 같습니다.

```text
gripper_joint_1
joint1
joint2
joint3
joint4
joint5
```

즉 로봇팔 본체는 Joint 1~5까지 5축이고,
그리퍼를 여섯 번째 동작축처럼 사용할 수 있습니다.

현재 기준 자세로 사용한 값은 다음과 같습니다.

```text
joint1 =  0.00000 rad
joint2 = -1.57233 rad
joint3 =  1.57233 rad
joint4 =  1.54318 rad
joint5 = -0.00153 rad
```

주의: 이 값은 제조사의 절대적인 공장 초기 자세가 아니라,
실제 로봇에서 `/joint_states`로 처음 읽은 자세를 오늘의 기준 자세로 사용한 것입니다.

---

# 3. 터미널 1 — OMX-F 로봇팔 시스템 실행

## 3-1. ROS 2 Jazzy 환경 불러오기

```bash
source /opt/ros/jazzy/setup.bash
```

이 명령은 현재 터미널에서 ROS 2 Jazzy 명령어를 사용할 수 있도록 환경을 설정합니다.

`source`는 프로그램을 새로 실행하는 명령이라기보다,
현재 터미널에 환경설정을 불러오는 명령입니다.

이 과정을 하지 않으면 다음 명령들이 정상적으로 인식되지 않을 수 있습니다.

```text
ros2
ros2 launch
ros2 topic
ros2 control
ros2 action
```

---

## 3-2. OMX 작업공간 불러오기

```bash
source ~/Robotics/ros2_ws/install/setup.bash
```

이 명령은 OpenManipulator OMX 관련 패키지가 설치된 ROS 2 작업공간을
현재 터미널 환경에 추가합니다.

`~`는 홈 디렉터리를 의미하므로 실제 경로는 대략 다음과 같습니다.

```text
/home/formakers/Robotics/ros2_ws/
```

이 작업공간을 source 해야 ROS 2가 다음과 같은 OMX 패키지를 찾을 수 있습니다.

```text
open_manipulator_bringup
```

---

## 3-3. USB 포트 확인

```bash
ls -l /dev/ttyACM*
```

OMX 컨트롤러가 `/dev/ttyACM0` 또는 `/dev/ttyACM1` 등 어느 포트에 연결되었는지 확인합니다.

예:

```text
/dev/ttyACM0
```

포트 번호는 USB 연결 순서에 따라 바뀔 수 있으므로,
로봇이 실행되지 않을 때 가장 먼저 확인해야 하는 항목 중 하나입니다.

---

## 3-4. OMX-F 실제 로봇팔 실행

```bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM0
```

이 명령은 실제 OMX-F 로봇 하드웨어와 ROS 2를 연결하고,
필요한 컨트롤러들을 실행합니다.

명령 구조:

```text
ros2 launch
```

ROS 2 launch 파일 실행

```text
open_manipulator_bringup
```

OpenManipulator 하드웨어 실행 패키지

```text
omx_f.launch.py
```

OMX-F 전용 launch 파일

```text
port_name:=/dev/ttyACM0
```

실제 로봇 컨트롤러가 연결된 USB 포트 지정

만약 포트가 `/dev/ttyACM1`이라면 다음처럼 바꿉니다.

```bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM1
```

---

## 3-5. 터미널 1 한 번에 실행

매번 한 줄씩 입력하지 않고 아래 세 줄을 한 번에 사용할 수 있습니다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch open_manipulator_bringup omx_f.launch.py port_name:=/dev/ttyACM0
```

터미널 1은 로봇을 사용하는 동안 종료하지 않습니다.

`Ctrl+C`로 종료하면 OMX-F 하드웨어 제어 시스템도 함께 종료됩니다.

---

# 4. 터미널 2 — 상태 확인 및 로봇 동작 명령

## 4-1. 터미널 2 환경 설정

새 터미널을 열면 다시 ROS 환경을 불러와야 합니다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash
```

터미널 1에서 source 했다고 해서 터미널 2까지 자동 적용되지는 않습니다.

---

## 4-2. 컨트롤러 상태 확인

```bash
ros2 control list_controllers
```

이 명령은 현재 로봇 제어에 사용되는 ROS 2 Controller 상태를 확인합니다.

정상적으로 실행 중이라면 arm_controller, joint_state_broadcaster,
gripper_controller 등이 active 상태로 보여야 합니다.

---

## 4-3. 하드웨어 인터페이스 확인

```bash
ros2 control list_hardware_interfaces
```

이 명령으로 Joint 1~5와 Gripper가 컨트롤러에 연결되어 있는지 확인합니다.

실제 확인된 주요 command interface는 다음과 같습니다.

```text
gripper_joint_1/position [available] [claimed]
joint1/position [available] [claimed]
joint2/position [available] [claimed]
joint3/position [available] [claimed]
joint4/position [available] [claimed]
joint5/position [available] [claimed]
```

`claimed`는 해당 인터페이스를 현재 컨트롤러가 사용 중이라는 뜻입니다.

---

## 4-4. 현재 실제 관절값 확인

```bash
ros2 topic echo /joint_states --once
```

이 명령은 현재 로봇의 Joint 위치를 한 번만 읽습니다.

실제 확인된 값:

```text
name:
- gripper_joint_1
- joint1
- joint2
- joint3
- joint4
- joint5

position:
- -0.04448544284889033
- -2.0694557179012918e-13
- -1.572330307582989
- 1.5723303075825754
- 1.5431846726127478
- -0.001533980788092748
```

이를 보기 좋게 정리하면:

```text
Gripper ≈ -0.04449
Joint 1 ≈  0.00000
Joint 2 ≈ -1.57233
Joint 3 ≈  1.57233
Joint 4 ≈  1.54318
Joint 5 ≈ -0.00153
```

---

# 5. JointTrajectory 명령의 구조 이해하기

Joint 1~5는 다음 Topic으로 명령합니다.

```text
/arm_controller/joint_trajectory
```

사용하는 메시지 형식은:

```text
trajectory_msgs/msg/JointTrajectory
```

기본 구조:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [값1, 값2, 값3, 값4, 값5],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

`--once`는 메시지를 한 번만 전송한다는 뜻입니다.

`joint_names` 배열의 순서와 `positions` 배열의 순서는 반드시 서로 대응해야 합니다.

즉:

```text
positions[0] → joint1
positions[1] → joint2
positions[2] → joint3
positions[3] → joint4
positions[4] → joint5
```

`time_from_start`가 2초라면 목표 위치까지 약 2초 동안 움직입니다.

---

# 6. Joint 1 동작

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.10, -1.57233, 1.57233, 1.54318, -0.00153],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

기준 위치:

```text
Joint 1 = 0.00
```

목표 위치:

```text
Joint 1 = 0.10
```

변화량은 +0.10 rad이며 약 5.7도입니다.

나머지 Joint 2~5는 기준 위치 그대로 유지합니다.

---

# 7. Joint 2 동작

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.47233, 1.57233, 1.54318, -0.00153],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

기준 위치:

```text
Joint 2 = -1.57233
```

목표 위치:

```text
Joint 2 = -1.47233
```

변화량은 +0.10 rad입니다.

중요한 점은 이 방식이 Joint 2 값만 보내는 것이 아니라
Joint 1~5의 전체 목표 자세를 다시 보내는 방식이라는 것입니다.

따라서 Joint 1이 다른 위치에 있었다면 이 명령을 실행하면서 Joint 1은 다시 0.0으로 돌아갑니다.

---

# 8. Joint 3 동작

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.57233, 1.67233, 1.54318, -0.00153],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

기준 위치:

```text
Joint 3 = 1.57233
```

목표 위치:

```text
Joint 3 = 1.67233
```

Joint 3는 로봇팔의 팔꿈치 자세 변화에 큰 영향을 줍니다.
처음에는 작은 변화량으로 테스트하는 것이 좋습니다.

반대 방향 테스트:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.57233, 1.47233, 1.54318, -0.00153],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

---

# 9. Joint 4 동작

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.57233, 1.57233, 1.64318, -0.00153],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

기준 위치:

```text
Joint 4 = 1.54318
```

목표 위치:

```text
Joint 4 = 1.64318
```

Joint 4는 로봇 끝단의 방향과 자세를 조정하는 데 중요한 역할을 합니다.

---

# 10. Joint 5 동작

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.57233, 1.57233, 1.54318, 0.10],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

Joint 5 기준값은 거의 0 rad입니다.

```text
Joint 5 ≈ -0.00153
```

테스트 목표값:

```text
Joint 5 = 0.10
```

Joint 5는 손목과 그리퍼 방향 조정에 사용되는 중요한 관절입니다.

---

# 11. Joint 6 — Gripper

OMX-F에서 편의상 여섯 번째 동작축으로 부르는 것은 Gripper입니다.

ROS 이름:

```text
gripper_joint_1
```

Gripper는 Joint 1~5와 다른 방식으로 Action 명령을 사용할 수 있습니다.

Action 확인:

```bash
ros2 action list | grep gripper
```

---

## 11-1. Gripper 열기

```bash
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.01, max_effort: 10.0}}"
```

`position: 0.01`은 그리퍼 목표 위치이고,
`max_effort: 10.0`은 최대 힘에 관련된 명령값입니다.

---

## 11-2. Gripper 닫기

```bash
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: -0.01, max_effort: 10.0}}"
```

`position`의 부호를 반대로 하여 반대 방향으로 움직이는 테스트입니다.

실제 허용 범위는 로봇의 기구와 컨트롤러 설정에 따라 달라질 수 있으므로
처음에는 작은 값부터 시험합니다.

---

# 12. 전체 기준 자세로 복귀

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],
  points: [{
    positions: [0.0, -1.57233, 1.57233, 1.54318, -0.00153],
    time_from_start: {sec: 3, nanosec: 0}
  }]
}"
```

이 명령은 Joint 1~5를 우리가 기준으로 잡은 자세로 한 번에 이동시킵니다.

```text
Joint 1 →  0.00000
Joint 2 → -1.57233
Joint 3 →  1.57233
Joint 4 →  1.54318
Joint 5 → -0.00153
```

3초에 걸쳐 이동하도록 설정하여 개별 테스트보다 조금 천천히 복귀합니다.

---

# 13. 전체 작업 흐름

```text
[터미널 1]
ROS 2 Jazzy 환경 로드
        ↓
OMX 작업공간 로드
        ↓
USB 포트 확인
        ↓
OMX-F bringup 실행
        ↓
로봇 하드웨어 + Controller 계속 실행


[터미널 2]
ROS 2 환경 로드
        ↓
Controller 상태 확인
        ↓
Joint State 확인
        ↓
Joint 1 테스트
        ↓
Joint 2 테스트
        ↓
Joint 3 테스트
        ↓
Joint 4 테스트
        ↓
Joint 5 테스트
        ↓
Gripper 테스트
        ↓
전체 기준 자세 복귀
```

---

# 14. 초보자가 꼭 이해해야 할 핵심

첫 번째, 터미널 1과 터미널 2는 역할이 다릅니다.

터미널 1은 로봇 시스템 자체를 실행하고,
터미널 2는 이미 실행된 시스템에 명령을 보내는 구조입니다.

두 번째, JointTrajectory 명령은 한 관절만 보내는 것이 아니라
Joint 1~5의 전체 목표값을 한 번에 지정합니다.

세 번째, 작은 값부터 움직이는 것이 안전합니다.

예를 들어:

```text
0.10 rad ≈ 5.7도
```

정도부터 시험하면 실제 로봇의 회전 방향을 확인하기 쉽습니다.

네 번째, USB 포트는 바뀔 수 있습니다.

```text
/dev/ttyACM0
/dev/ttyACM1
```

로봇이 실행되지 않으면 먼저 포트를 확인합니다.

다섯 번째, `/joint_states`는 현재 로봇의 실제 자세를 확인하는 가장 중요한 자료 중 하나입니다.

---

# 15. 앞으로 확장할 수 있는 단계

이 기본 제어가 안정되면 다음 단계로 확장할 수 있습니다.

1. Python으로 JointTrajectory 자동 전송
2. 키보드로 Joint 1~5 수동 조작
3. 여러 Pose 저장 및 재생
4. HOME → A → B → HOME 자동 시퀀스
5. MoveIt IK 연결
6. 카메라 좌표와 로봇 좌표 연결
7. YOLO 물체 인식 결과를 로봇 목표점으로 사용
8. Depth Camera를 이용한 3D 좌표 계산
9. 물체 인식 → 접근 → Gripper 닫기 → 들어올리기 자동화

이 과정을 통해 단순한 “모터 움직이기”에서
실제 AI 비전 기반 로봇 조작 시스템으로 발전시킬 수 있습니다.

---

# 16. GitHub 업로드 예시

FOR-MAKERS-LAB 저장소 안에 새 프로젝트 폴더를 만드는 예시입니다.

```bash
cd ~/FOR-MAKERS-LAB
mkdir -p 2026-08-22-omx-robot-arm-terminal-guide
```

책 파일을 해당 폴더에 `BOOK.md`라는 이름으로 저장합니다.

이후 Git 상태 확인:

```bash
git status
```

파일 추가:

```bash
git add 2026-08-22-omx-robot-arm-terminal-guide/BOOK.md
```

Commit:

```bash
git commit -m "Add OMX-F robot arm terminal control guide"
```

GitHub로 Push:

```bash
git push origin main
```

마지막으로 기록 확인:

```bash
git log --oneline -5
```

---

# 마무리

이번 작업의 핵심은 단순히 OMX-F 로봇팔을 한 번 움직여 보는 것이 아닙니다.

ROS 2에서 실제 로봇이 어떤 구조로 실행되고,
Controller가 어떻게 Joint를 소유하며,
Topic과 Action을 통해 어떻게 명령을 전달하는지 이해하는 것이 중요합니다.

터미널 1에서 하드웨어 시스템을 실행하고,
터미널 2에서 JointTrajectory와 Gripper Action을 보내는 구조를 이해하면
앞으로 Python 자동제어, MoveIt, YOLO, Depth Camera와도 자연스럽게 연결할 수 있습니다.

**FOR MAKERS LAB — OMX-F Robot Arm Practice**
