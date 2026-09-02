# ROBOTIS OMX-F Episode 데이터 수집과 자동 재생 실습서

## 사람의 시범 동작을 로봇 데이터로 만들고 다시 재현하기

- 날짜: 2026-09-03
- 대상: ROBOTIS OMX-F
- 환경: Ubuntu + ROS 2 Jazzy
- 핵심 주제: 키보드 티칭 → Episode 기록 → CSV 저장 → Episode 자동 재생

---

## 1. 오늘 무엇을 공부했는가

오늘의 목표는 단순히 OMX-F를 키보드로 움직이는 것이 아니었다.

사람이 로봇을 직접 움직여 하나의 작업을 가르치고, 그 움직임을 시간에 따른 관절 데이터로 기록한 뒤, 저장된 데이터를 다시 읽어서 로봇이 자동으로 같은 움직임을 재현하는 전체 과정을 이해하는 것이 목표였다.

전체 흐름은 다음과 같다.

```text
사람
 ↓
키보드 조작
 ↓
OMX-F 로봇팔
 ↓
/joint_states
 ↓
Episode 데이터 기록
 ↓
episode_001.csv
episode_002.csv
episode_003.csv
 ↓
자동 재생 프로그램
 ↓
OMX-F가 저장된 동작 재현
```

즉 오늘의 핵심은

> 사람의 움직임 → 로봇 데이터 → 다시 로봇의 움직임

이라는 로봇 데이터 파이프라인을 직접 구현해 보는 것이었다.

---

## 2. 전체 시스템 구조

```text
┌───────────────────────────────┐
│ Terminal 1                    │
│ OMX-F Bringup                 │
│ ROS 2 ↔ 실제 로봇 하드웨어     │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ Terminal 2                    │
│ Keyboard Teleoperation        │
│ 사람이 Joint 1~5 + Gripper 조작│
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ Terminal 3                    │
│ record_joint_data.py          │
│ /joint_states 기록            │
│ R = Record / S = Save         │
└──────────────┬────────────────┘
               │
               ▼
       ┌─────────────────┐
       │ Episode CSV     │
       │ 001 / 002 / 003 │
       └────────┬────────┘
                │
                ▼
┌───────────────────────────────┐
│ Terminal 4                    │
│ play_all_episodes.py          │
│ CSV → ROS 2 → OMX-F            │
└──────────────┬────────────────┘
               │
               ▼
        자동 동작 재현
```

---

# 3. Terminal 1 — OMX-F Bringup

터미널 1의 역할은 실제 OMX-F를 ROS 2에서 사용할 수 있도록 연결하고 컨트롤러를 실행하는 것이다.

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py \
port_name:=/dev/ttyACM1
```

### 명령어 의미

```text
cd ~/Robotics/ros2_ws
```

ROS 2 작업공간으로 이동한다.

```text
source install/setup.bash
```

빌드된 ROS 2 패키지와 환경 설정을 현재 터미널에 적용한다.

```text
ros2 launch open_manipulator_bringup omx_f.launch.py
```

OMX-F에 필요한 ROS 2 노드와 컨트롤러를 실행한다.

```text
port_name:=/dev/ttyACM1
```

현재 Follower가 연결된 USB 시리얼 포트를 지정한다.

### ACM 번호에 대한 주의

`/dev/ttyACM0`, `/dev/ttyACM1`은 로봇에 영구적으로 고정된 번호가 아니다. USB 연결 순서나 재연결에 따라 번호가 바뀔 수 있다.

확인은 다음처럼 할 수 있다.

```bash
ls -l /dev/ttyACM*
```

따라서 핵심은 “ACM1이 항상 Follower”가 아니라, 현재 Follower가 어떤 포트로 인식됐는지를 확인하고 그 값을 `port_name`에 넣는 것이다.

---

# 4. Terminal 2 — Keyboard Teleoperation

터미널 2는 사람이 로봇에게 동작을 가르치는 단계다.

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 run open_manipulator_teleop omx_f_teleop
```

키보드 조작은 다음과 같다.

```text
1 / q  → Joint 1
2 / w  → Joint 2
3 / e  → Joint 3
4 / r  → Joint 4
5 / t  → Joint 5

o / p  → Gripper

ESC    → 종료
```

각 키를 이용해 관절을 움직여 작업 경로를 만든다.

예:

```text
HOME
 ↓
물체 접근
 ↓
그리퍼 조작
 ↓
물체 잡기
 ↓
이동
 ↓
놓기
 ↓
HOME
```

이 단계에서는 아직 AI가 판단하는 것이 아니다. 사람이 직접 시범 동작을 만드는 것이다.

---

# 5. Terminal 3 — Episode 데이터 기록

터미널 3은 사람이 가르친 로봇 움직임을 데이터로 기록한다.

실행:

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 record_joint_data.py
```

프로그램 명령:

```text
R + Enter → 기록 시작
S + Enter → 저장
Q + Enter → 종료
```

### 실제 기록 순서

```text
R + Enter
 ↓
Episode 기록 시작
 ↓
Terminal 2에서 로봇 조작
 ↓
HOME → 접근 → 잡기 → 이동 → 놓기
 ↓
Terminal 3으로 돌아옴
 ↓
S + Enter
 ↓
episode_001.csv 생성
```

다시 반복하면:

```text
R → 동작 → S
     ↓
episode_002.csv

R → 동작 → S
     ↓
episode_003.csv
```

### 중요한 개념

Episode 하나는 특정 위치 하나가 아니다.

`R`을 누른 순간부터 `S`를 누른 순간까지의 전체 작업 과정이 하나의 Episode다.

---

# 6. CSV 파일 구조

각 Episode CSV의 기본 구조는 다음과 같다.

```text
time,joint1,joint2,joint3,joint4,joint5,gripper
```

예:

```text
0.00,0.10,-1.02,0.82,1.40,0.02,0.20
0.05,0.11,-1.03,0.83,1.41,0.02,0.20
0.10,0.13,-1.05,0.85,1.42,0.03,0.21
```

### time

Episode 시작 이후 경과 시간이다.

```text
0.00
0.05
0.10
0.15
...
```

### joint1 ~ joint5

OMX-F 각 관절의 현재 `position` 값이다.

현재 기록 프로그램은 ROS 2 `/joint_states`의 `position` 값을 그대로 저장한다. 따라서 일반적으로 라디안 단위의 관절 위치값으로 이해하는 것이 맞다.

### gripper

그리퍼 관절의 현재 위치값이다.

따라서 CSV 한 줄은

> “이 시간에 로봇이 이런 관절 자세였다.”

라는 하나의 시점 데이터를 의미한다.

이런 데이터가 시간 순서대로 수백~수천 줄 쌓이면 하나의 로봇 작업 경로가 된다.

---

# 7. record_joint_data.py 전체 코드

```python
#!/usr/bin/env python3

import os
import csv
import time
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class OMXEpisodeRecorder(Node):

    def __init__(self):
        super().__init__('omx_episode_recorder')

        self.save_dir = os.path.expanduser('~/omx_dataset')
        os.makedirs(self.save_dir, exist_ok=True)

        self.joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5',
            'gripper_joint_1'
        ]

        self.recording = False
        self.rows = []
        self.start_time = None

        self.episode_number = self.find_next_episode()

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        print()
        print('========================================')
        print(' OMX-F EPISODE DATA RECORDER')
        print('========================================')
        print(' R + Enter : 기록 시작')
        print(' S + Enter : 저장')
        print(' Q + Enter : 종료')
        print('========================================')
        print(f'다음 Episode : {self.episode_number:03d}')
        print('========================================')
        print()

        self.keyboard_thread = threading.Thread(
            target=self.keyboard_loop,
            daemon=True
        )
        self.keyboard_thread.start()

    def find_next_episode(self):

        episode = 1

        while True:

            filename = os.path.join(
                self.save_dir,
                f'episode_{episode:03d}.csv'
            )

            if not os.path.exists(filename):
                return episode

            episode += 1

    def keyboard_loop(self):

        while rclpy.ok():

            try:
                command = input(
                    '명령 [R=기록 / S=저장 / Q=종료] > '
                )

            except EOFError:
                break

            command = command.strip().lower()

            if command == 'r':
                self.start_recording()

            elif command == 's':
                self.stop_and_save()

            elif command == 'q':

                if self.recording:
                    print()
                    print('현재 기록 중입니다.')
                    print('먼저 S + Enter로 저장하세요.')
                    continue

                print()
                print('프로그램 종료')

                rclpy.shutdown()
                break

            else:
                print()
                print('R, S 또는 Q를 입력하세요.')

    def start_recording(self):

        if self.recording:
            print()
            print('이미 기록 중입니다.')
            return

        self.rows = []
        self.start_time = time.time()
        self.recording = True

        print()
        print('========================================')
        print(f' EPISODE {self.episode_number:03d}')
        print(' RECORDING START')
        print('========================================')
        print('이제 터미널 2에서 로봇을 움직이세요.')
        print()

    def stop_and_save(self):

        if not self.recording:
            print()
            print('현재 기록 중인 Episode가 없습니다.')
            return

        self.recording = False

        filename = os.path.join(
            self.save_dir,
            f'episode_{self.episode_number:03d}.csv'
        )

        with open(filename, 'w', newline='') as f:

            writer = csv.writer(f)

            writer.writerow([
                'time',
                'joint1',
                'joint2',
                'joint3',
                'joint4',
                'joint5',
                'gripper'
            ])

            writer.writerows(self.rows)

        print()
        print('========================================')
        print(' EPISODE 저장 완료')
        print('========================================')
        print(f'파일 : {filename}')
        print(f'데이터 수 : {len(self.rows)} samples')
        print('========================================')

        self.episode_number += 1

        print()
        print(
            f'다음 Episode : '
            f'episode_{self.episode_number:03d}.csv'
        )
        print()

        self.rows = []

    def joint_callback(self, msg):

        if not self.recording:
            return

        joint_data = dict(
            zip(msg.name, msg.position)
        )

        elapsed = time.time() - self.start_time

        row = [elapsed]

        for name in self.joint_names:

            row.append(
                joint_data.get(
                    name,
                    float('nan')
                )
            )

        self.rows.append(row)

        count = len(self.rows)

        if count % 20 == 0:

            self.get_logger().info(
                f'Episode {self.episode_number:03d} '
                f'| {count} samples '
                f'| {elapsed:.2f} sec'
            )


def main(args=None):

    rclpy.init(args=args)

    node = OMXEpisodeRecorder()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        if node.recording:
            print()
            print(
                '기록 중 종료되었습니다. '
                '현재 Episode는 저장되지 않았습니다.'
            )

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 8. Terminal 4 — All Episode 자동 재생

터미널 4는 저장된 데이터를 다시 로봇의 움직임으로 바꾸는 단계다.

실행:

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 play_all_episodes.py
```

프로그램은 `~/omx_dataset` 안에서 `episode_*.csv` 파일을 자동으로 찾는다.

예:

```text
episode_001.csv
episode_002.csv
episode_003.csv
```

그리고 번호 순서대로 재생한다.

```text
Episode 001
 ↓
3초 대기
 ↓
Episode 002
 ↓
3초 대기
 ↓
Episode 003
 ↓
종료
```

현재 버전은 한 번 재생한 뒤 종료한다. 무한 반복 방식이 아니다.

---

# 9. play_all_episodes.py 전체 코드

```python
#!/usr/bin/env python3

import csv
import glob
import os
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.action import GripperCommand


class OMXMultiEpisodePlayer(Node):

    def __init__(self):
        super().__init__('omx_multi_episode_player')

        self.arm_joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5'
        ]

        self.arm_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            '/gripper_controller/gripper_cmd'
        )

        self.get_logger().info(
            'OMX-F Multi Episode Player Ready'
        )

    def send_arm(self, joint_positions, duration):

        msg = JointTrajectory()
        msg.joint_names = self.arm_joint_names

        point = JointTrajectoryPoint()
        point.positions = joint_positions

        duration = max(duration, 0.08)

        sec = int(duration)
        nanosec = int((duration - sec) * 1e9)

        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        msg.points.append(point)

        self.arm_pub.publish(msg)

    def send_gripper(self, position):

        if not self.gripper_client.wait_for_server(
            timeout_sec=0.2
        ):
            return

        goal = GripperCommand.Goal()

        goal.command.position = position
        goal.command.max_effort = 20.0

        self.gripper_client.send_goal_async(goal)


def load_episode(filename):

    data = []

    with open(filename, 'r', newline='') as f:

        reader = csv.DictReader(f)

        for row in reader:

            try:

                data.append({
                    'time': float(row['time']),

                    'joints': [
                        float(row['joint1']),
                        float(row['joint2']),
                        float(row['joint3']),
                        float(row['joint4']),
                        float(row['joint5'])
                    ],

                    'gripper': float(row['gripper'])
                })

            except (ValueError, KeyError) as e:

                print(
                    f'잘못된 데이터 건너뜀 : {e}'
                )

    return data


def play_episode(
    node,
    filename,
    speed_scale=0.5
):

    data = load_episode(filename)

    if not data:
        print(
            f'{os.path.basename(filename)} : 데이터 없음'
        )
        return

    print()
    print('========================================')
    print(
        f' PLAY START : {os.path.basename(filename)}'
    )
    print('========================================')
    print(f'Samples : {len(data)}')
    print(f'Speed   : {speed_scale}')
    print()

    previous_time = data[0]['time']

    for index, row in enumerate(data):

        current_time = row['time']

        dt = current_time - previous_time

        if dt < 0:
            dt = 0

        sleep_time = dt / speed_scale

        node.send_arm(
            row['joints'],
            max(0.08, sleep_time)
        )

        node.send_gripper(
            row['gripper']
        )

        rclpy.spin_once(
            node,
            timeout_sec=0.001
        )

        if sleep_time > 0:
            time.sleep(sleep_time)

        previous_time = current_time

        if index % 20 == 0:

            print(
                f'PLAY '
                f'{index}/{len(data)} '
                f'| time={current_time:.2f}'
            )

    print()
    print('----------------------------------------')
    print(
        f'{os.path.basename(filename)} COMPLETE'
    )
    print('----------------------------------------')


def main():

    rclpy.init()

    node = OMXMultiEpisodePlayer()

    dataset_dir = os.path.expanduser(
        '~/omx_dataset'
    )

    episode_files = sorted(
        glob.glob(
            os.path.join(
                dataset_dir,
                'episode_*.csv'
            )
        )
    )

    print()
    print('========================================')
    print(' OMX-F ALL EPISODES AUTO PLAYBACK')
    print('========================================')

    if not episode_files:

        print()
        print('Episode 파일이 없습니다.')
        print('~/omx_dataset/episode_*.csv')

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

        return

    print()
    print(
        f'발견된 Episode : '
        f'{len(episode_files)}개'
    )
    print()

    for filename in episode_files:

        print(
            ' -',
            os.path.basename(filename)
        )

    print()
    print('========================================')
    print('5초 후 자동 재생 시작')
    print('로봇 주변을 확인하세요.')
    print('========================================')
    print()

    time.sleep(5)

    speed_scale = 0.5
    episode_wait = 3.0

    for index, filename in enumerate(
        episode_files
    ):

        print()
        print(
            f'>>> Episode '
            f'{index + 1}/{len(episode_files)}'
        )

        play_episode(
            node,
            filename,
            speed_scale
        )

        if index < len(episode_files) - 1:

            print()
            print(
                f'다음 Episode까지 '
                f'{episode_wait:.0f}초 대기...'
            )

            time.sleep(
                episode_wait
            )

    print()
    print('========================================')
    print(' ALL EPISODES PLAYBACK COMPLETE')
    print('========================================')
    print()

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 10. 최종 실행 순서

## Terminal 1

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py \
port_name:=/dev/ttyACM1
```

## Terminal 2

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 run open_manipulator_teleop omx_f_teleop
```

## Terminal 3

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 record_joint_data.py
```

```text
R + Enter
→ Terminal 2에서 로봇 조작
→ Terminal 3에서 S + Enter
```

## Terminal 4

```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 play_all_episodes.py
```

---

# 11. 오늘 배운 핵심

오늘 만든 시스템을 가장 간단하게 표현하면 다음과 같다.

```text
TERMINAL 1
로봇 연결
    ↓
TERMINAL 2
사람이 로봇을 움직임
    ↓
TERMINAL 3
움직임을 데이터로 기록
    ↓
EPISODE CSV
    ↓
TERMINAL 4
데이터를 읽어서
로봇이 다시 움직임
```

즉,

> 사람이 로봇에게 동작을 가르친다.
>
> 로봇의 움직임이 데이터가 된다.
>
> 데이터가 다시 로봇의 행동이 된다.

이것이 오늘의 가장 중요한 학습 내용이다.

---

# 12. 앞으로의 발전 방향

현재 시스템은 저장된 관절 궤적을 그대로 재생하는 단계다.

다음 단계에서는 여기에 RGB/Depth 카메라를 추가할 수 있다.

```text
RGB Camera
     +
Depth Camera
     +
Joint State
     +
Gripper
     ↓
Episode Dataset
     ↓
물체 인식
     ↓
3D 위치 계산
     ↓
좌표 변환
     ↓
로봇 제어
```

더 나아가 여러 Episode를 이용해 로봇 학습 데이터를 만들고, 학습된 정책이 환경을 보고 적절한 행동을 선택하도록 발전시킬 수 있다.

따라서 오늘의 실습은 단순한 키보드 조작 실습이 아니라,

**Robot Teleoperation → Demonstration Data → Dataset → Playback → Robot Learning**

으로 발전하는 과정의 첫 번째 기본 단계다.
