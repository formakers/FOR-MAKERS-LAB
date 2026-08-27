# ROBOTIS OMX Leader–Follower Record & Smooth Playback

이 폴더는 실제 테스트에서 사용한 구조를 기준으로 정리한 GitHub 업로드용 프로젝트입니다.

## 하드웨어 기준

- Leader OMX-L: `/dev/ttyACM0`
- Follower OMX-F: `/dev/ttyACM1`
- ROS 2: Jazzy
- Workspace: `~/Robotics/ros2_ws`

> USB를 다시 연결하면 `ttyACM0/1` 번호가 바뀔 수 있으므로 먼저 `ls -l /dev/ttyACM*`로 확인하세요.

---

## 전체 구조

### Teaching / Recording
터미널 1 + 터미널 2 + 터미널 3을 사용합니다.

```text
Leader OMX-L
    ↓ /leader/joint_states
Follow + Record Python
    ├─→ Follower OMX-F
    └─→ omx_motion_v2.csv
```

### Smooth Playback
터미널 1과 터미널 3을 종료하고, 터미널 2 + 터미널 4만 사용합니다.

```text
omx_motion_v2.csv
    ↓
Smooth Playback Python
    ↓
Follower OMX-F
```

> 재생 시 Leader를 켜두면 `/leader/joint_trajectory` publisher가 서로 충돌할 수 있으므로 반드시 Leader와 Record 프로그램을 종료하세요.

---

# 터미널 1 — Leader OMX-L

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

ros2 launch open_manipulator_bringup \
omx_l_leader_ai.launch.py \
port_name:=/dev/ttyACM0
```

---

# 터미널 2 — Follower OMX-F

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

ros2 launch open_manipulator_bringup \
omx_f_follower_ai.launch.py \
port_name:=/dev/ttyACM1
```

컨트롤러 확인:

```bash
ros2 control list_controllers
```

정상 예:

```text
joint_state_broadcaster    active
arm_controller             active
```

---

# 터미널 3 — Follow + Record

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

cd ~/omx_motion_test
python3 omx_follow_record_v2.py
```

키:

- `O` : Leader Gripper OPEN 위치 저장
- `C` : Leader Gripper CLOSE 위치 저장
- `G` : Follow + Record 시작
- `S` : Follow 정지
- `Q` : 종료

저장 파일:

```text
omx_motion_v2.csv
```

---

# 터미널 4 — Smooth Playback

재생 전:

- 터미널 1 Leader 종료
- 터미널 3 Follow/Record 종료
- 터미널 2 Follower 유지

실행:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Robotics/ros2_ws/install/setup.bash

cd ~/omx_motion_test
python3 omx_playback_smooth_v2.py
```

키:

- `1` : 1회 재생
- `5` : 5회 반복
- `0` : 무한 반복
- `S` : 정지
- `Q` : 종료

---

## 파일 구성

```text
2026-08-27-omx-leader-follower-record-playback/
├── README.md
├── terminal1_leader.sh
├── terminal2_follower.sh
├── terminal3_record.sh
├── terminal4_playback.sh
├── omx_follow_record_v2.py
├── omx_playback_smooth_v2.py
├── GITHUB_UPLOAD_COMMANDS.md
└── ROBOTIS_OMX_Leader_Follower_Record_Playback_Guide.docx
```
