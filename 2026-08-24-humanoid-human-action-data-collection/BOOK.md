# 휴머노이드 학습용 인간 행동 데이터 수집 시스템 — 상세 학습 노트

## 1. 프로젝트 개요

휴머노이드와 로봇팔이 사람처럼 작업하려면 단순한 이미지 데이터만으로는 부족합니다.
사람이 물체에 접근하고, 손가락을 닫고, 물체를 이동시키고, 다시 손을 여는 일련의 시간적 행동을 데이터로 수집해야 합니다.

이 프로젝트는 사람의 작업 행동을 다음 세 가지 축으로 측정합니다.

1. **Hand/Finger Motion** — 센서 장갑과 IMU
2. **Environment/Objects** — RGB/Depth 카메라와 객체 인식
3. **Robot State/Action** — ROS2를 통한 관절 상태 및 제어 명령

이 세 종류를 같은 시간축에 맞춰 저장하면 로봇 학습용 Demonstration Dataset의 기초가 됩니다.

---

## 2. 센서 장갑

Flex Sensor는 손가락의 굽힘 정도를 전기 저항 변화로 표현합니다.
IMU는 손목 또는 손등의 자세와 회전 운동을 측정합니다.

초기 장갑에서 가장 중요한 것은 정밀도가 아니라 **반복 가능성과 캘리브레이션**입니다.
사용자가 손을 완전히 폈을 때와 최대한 구부렸을 때의 값을 각각 기록해 0~1 범위로 정규화하면 로봇 연동이 쉬워집니다.

예:

```text
normalized = (raw - min_value) / (max_value - min_value)
```

각 사용자와 장갑 착용 위치가 달라질 수 있으므로 캘리브레이션은 데이터 수집 세션마다 수행하는 편이 안전합니다.

---

## 3. 카메라와 3D 위치

RGB 카메라는 물체의 종류와 장면 정보를 제공합니다.
Depth 카메라는 각 픽셀까지의 거리를 측정할 수 있어 손과 물체를 3차원 좌표로 변환하는 데 사용할 수 있습니다.

예를 들어 YOLO가 컵의 중심 픽셀 `(u, v)`를 찾으면,
Depth 값 `Z`와 카메라 내부 파라미터를 사용하여 3차원 위치 `(X, Y, Z)`를 계산할 수 있습니다.

따라서:

```text
RGB → Object Detection
Depth → Distance
Camera Intrinsics → 3D Position
```

이라는 흐름이 됩니다.

---

## 4. 시간 동기화

로봇 학습 데이터에서 시간 동기화는 센서 종류만큼 중요합니다.

장갑, 카메라, Depth, YOLO, 로봇 상태가 서로 다른 주기로 들어오기 때문에
각 데이터에 timestamp를 기록한 뒤 가장 가까운 시점끼리 정렬하거나 보간해야 합니다.

예:

```text
t = 12.000
  glove:  11.999
  imu:    12.001
  rgb:    12.000
  depth:  12.000
  robot:  12.002
```

이렇게 정렬해야 “그 순간 사람이 어떤 손 모양을 하고 있었고 어떤 물체를 보고 있었는지”를 정확히 연결할 수 있습니다.

---

## 5. Episode

하나의 사진보다 하나의 작업 과정 전체가 훨씬 중요합니다.

예를 들어 컵 집기:

```text
Approach
→ Open Hand
→ Contact
→ Close Fingers
→ Lift
→ Move
→ Place
→ Release
```

이 전체 시퀀스를 Episode 하나로 저장합니다.

Episode가 많아질수록 다양한 속도, 위치, 접근 방향, 실패/성공 상황을 포함할 수 있습니다.

---

## 6. Retargeting

사람의 관절 구조와 로봇의 관절 구조는 동일하지 않습니다.
따라서 사람의 손동작을 로봇 관절로 변환하는 중간 단계가 필요합니다.

대표 흐름:

```text
Human Sensor Values
→ Calibration
→ Normalization
→ Human Pose
→ Robot Pose Mapping
→ IK / Joint Mapping
→ Robot Command
```

이 과정이 Teleoperation과 Demonstration 수집의 핵심입니다.

---

## 7. ROS2 통합 아이디어

초기에는 아래처럼 노드를 나누면 이해하기 쉽습니다.

```text
glove_driver_node
imu_node
camera_node
object_detection_node
sync_node
dataset_recorder_node
retargeting_node
robot_command_node
```

예시 Topic:

```text
/glove/fingers
/glove/imu
/vision/rgb
/vision/depth
/vision/object_pose
/human/hand_pose
/robot/joint_states
/robot/joint_command
```

ROS2의 장점은 센서, 비전, 데이터 저장, 로봇 제어를 독립적인 모듈로 개발한 뒤 하나의 시스템으로 연결할 수 있다는 점입니다.

---

## 8. 데이터 품질 체크

좋은 데이터셋을 만들려면 아래 항목을 확인해야 합니다.

- Timestamp가 단조 증가하는가
- 센서 드롭이 발생하지 않는가
- Flex Sensor 값이 포화되지 않는가
- IMU 방향이 갑자기 튀지 않는가
- RGB와 Depth가 동일 장면을 가리키는가
- 객체 ID가 프레임 사이에서 안정적인가
- Episode 시작/종료가 정확한가
- 로봇 상태와 인간 동작이 같은 시간축에 있는가

---

## 9. 첫 번째 실험

가장 추천하는 첫 번째 실험:

```text
Task: 검지 굽힘 기록
Device: ESP32 + Flex Sensor 1개
Output: CSV
Duration: 30초
```

CSV 예:

```csv
timestamp,index
0.000,0.05
0.010,0.07
0.020,0.18
0.030,0.41
0.040,0.72
```

이 작은 실험이 성공하면 다섯 손가락으로 확장하고, 그다음 IMU를 추가합니다.

---

## 10. 최종 목표

최종적으로는 다음과 같은 시스템을 목표로 합니다.

```text
Human Demonstration
  ↓
Sensor Glove + Vision
  ↓
Synchronized Multimodal Dataset
  ↓
Robot Retargeting
  ↓
Policy Learning
  ↓
Autonomous Robot / Humanoid
```

사람의 행동을 계측하고, 정리하고, 학습 데이터로 만드는 전체 파이프라인을 이해하는 것이 이 프로젝트의 핵심 학습 목표입니다.
