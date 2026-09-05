# AI가 움직이는 OMX 로봇팔 만들기
## OMX × ACT 모방학습 실전 기록 — 2026-09-06

## 1. 프로젝트의 의미

이 프로젝트는 미리 작성한 관절 궤적을 단순 재생하는 것이 아니라, 사람이 보여준 시범에서 학습한 ACT 정책이 **현재 카메라 영상 + 현재 로봇 상태**를 받아 다음 행동을 예측하고 실제 OMX를 움직이게 하는 과정이다.

```text
사람의 시범
  ↓
카메라 영상 + 관절 상태 + 행동
  ↓
LeRobot Dataset
  ↓
Google Colab / ACT 학습
  ↓
model.safetensors
  ↓
현재 RGB 영상 + 현재 6축 상태
  ↓
ACT Policy
  ↓
joint1~5 + gripper action
  ↓
안전 제한
  ↓
ROS 2 Controller
  ↓
실제 OMX
  └────────→ 다시 관측(Closed Loop)
```

![OMX × ACT 시스템 설계도](images/01-omx-act-system-design.png)

## 2. 학습 모델 다운로드 및 확인

Google Drive에서 받은 ZIP:

```text
pretrained_model-20260905T222536Z-1-001.zip
```

압축 해제:

```bash
cd ~/Downloads
unzip pretrained_model-20260905T222536Z-1-001.zip -d pretrained_model
find pretrained_model -maxdepth 4 -type f | sort
```

확인된 핵심 파일:

```text
config.json
model.safetensors
policy_preprocessor.json
policy_preprocessor_step_3_normalizer_processor.safetensors
policy_postprocessor.json
policy_postprocessor_step_0_unnormalizer_processor.safetensors
train_config.json
```

설정에서 확인된 ACT 구조:

```text
policy type      : act
observation.state: shape [6]
RGB image        : shape [3, 480, 640]
action           : shape [6]
chunk_size       : 100
n_action_steps   : 100
vision backbone  : ResNet18
dim_model        : 512
normalization    : STATE/ACTION = MEAN_STD
```

학습 데이터 설정에는 다음 경로/ID가 기록되어 있었다.

```text
repo_id: formakers/omx_camera_demo_new
root: /content/drive/MyDrive/omx/omx_camera_lerobot_v3_new
```

## 3. 로컬 AI 환경

사용한 가상환경:

```bash
source ~/omx_ai_venv/bin/activate
```

설치 후 확인된 주요 패키지:

```text
lerobot 0.6.1
torch 2.11.0
torchvision 0.26.0
safetensors 0.8.0
```

GPU 확인 당시:

```text
NVIDIA T600
VRAM 4096 MiB
CUDA available
```

ACT 모델 로딩 테스트:

```bash
cd ~/Downloads/pretrained_model/pretrained_model

python - <<'PY'
from lerobot.policies.act.modeling_act import ACTPolicy

policy = ACTPolicy.from_pretrained(".")
print("MODEL LOAD SUCCESS")
print(type(policy))
PY
```

실제 결과:

```text
Loading weights from local directory
MODEL LOAD SUCCESS
<class 'lerobot.policies.act.modeling_act.ACTPolicy'>
```

가짜 state/image를 이용한 첫 추론에서도 6차원 action 출력에 성공했다.

## 4. ROS 2와 Orbbec 카메라

ROS 환경:

```bash
source ~/Robotics/ros2_ws/install/setup.bash
```

Orbbec 패키지:

```bash
ros2 pkg list | grep orbbec
```

확인:

```text
orbbec_camera
orbbec_camera_msgs
orbbec_description
```

소스의 Gemini 330 launch:

```text
~/Robotics/ros2_ws/src/OrbbecSDK_ROS2/orbbec_camera/launch/gemini_330_series.launch.py
```

카메라 실행 예:

```bash
source ~/Robotics/ros2_ws/install/setup.bash
ros2 launch \
~/Robotics/ros2_ws/src/OrbbecSDK_ROS2/orbbec_camera/launch/gemini_330_series.launch.py
```

확인된 토픽:

```text
/camera/color/camera_info
/camera/color/image_raw
/camera/depth/camera_info
/camera/depth/image_raw
/camera/depth/points
```

실험 중 RGB 토픽은 약 21~23 Hz가 관측되었다.

```bash
ros2 topic hz /camera/color/image_raw
```

## 5. OMX 관절 상태

```bash
ros2 topic echo /joint_states --once
```

관절 순서:

```text
gripper_joint_1
joint1
joint2
joint3
joint4
joint5
```

ACT에는 다음 순서로 재배열하여 6차원 state를 넣었다.

```text
[joint1, joint2, joint3, joint4, joint5, gripper_joint_1]
```

실험 중 `/joint_states`는 약 100 Hz로 들어왔다.

## 6. ACT와 실제 센서 연결

실제 RGB 영상과 현재 6축 state를 ACT에 입력했을 때 action 출력에 성공했다.

예:

```text
STATE
[-0.     -1.5723  1.5693  1.5401  0.0077  0.698 ]

ACT ACTION
[[-0.0021 -1.2248  1.3495  1.2808  0.0024  0.7126]]
```

이 단계에서는 `NO COMMAND SENT TO ROBOT`으로 실제 명령을 막고 추론만 검증했다.

## 7. 실제 OMX 명령 연결

ARM:

```text
/arm_controller/joint_trajectory
```

Gripper:

```text
/gripper_controller/gripper_cmd
```

실제 확인:

```text
/arm_controller/joint_trajectory
Publisher count: 1
Subscription count: 1

/gripper_controller/gripper_cmd
Action servers: 1
```

실제 구동 중 예:

```text
STATE
[ 0.0215 -1.0216  1.241   1.2349 -0.0138  0.7179]

ACT TARGET
[ 0.0334 -1.0305  1.1579  1.2329 -0.0144  0.7189]

SAFE ARM
[ 0.0334 -1.0305  1.191   1.2329 -0.0144]

SAFE GRIPPER
0.7189

ARM COMMAND SENT
GRIPPER COMMAND SENT
```

## 8. Left / Center / Right 컵 위치 실험

로봇 자세는 그대로 유지하고 컵만 이동했다. 진단 코드는 로봇 명령을 전혀 보내지 않고 각 위치에서 ACT를 10회 추론했다.

### RIGHT

```text
ROBOT STATE
[-0.0583 -0.6400  0.8866  1.2226 -0.1135  0.6934]

ACT MEAN
[-0.0128 -0.4436  0.7416  1.1875 -0.0672  0.6912]

ACT STD
[0.0020 0.0058 0.0058 0.0035 0.0018 0.0013]
```

### CENTER

```text
ROBOT STATE
[-0.0583 -0.6398  0.8866  1.2226 -0.1135  0.6934]

ACT MEAN
[-0.0299 -0.6745  0.9242  1.2553 -0.0710  0.7027]

ACT STD
[0.0015 0.0049 0.0039 0.0027 0.0013 0.0011]
```

### LEFT

```text
ROBOT STATE
[-0.0583 -0.6401  0.8866  1.2226 -0.1135  0.6934]

ACT MEAN
[-0.0567 -0.2812  0.5770  1.0975 -0.1380  0.6486]

ACT STD
[0.0018 0.0053 0.0085 0.0050 0.0027 0.0018]
```

### 비교

| Cup | J1 | J2 | J3 | J4 | J5 | Gripper |
|---|---:|---:|---:|---:|---:|---:|
| Left | -0.0567 | -0.2812 | 0.5770 | 1.0975 | -0.1380 | 0.6486 |
| Center | -0.0299 | -0.6745 | 0.9242 | 1.2553 | -0.0710 | 0.7027 |
| Right | -0.0128 | -0.4436 | 0.7416 | 1.1875 | -0.0672 | 0.6912 |

로봇 state가 거의 같은데 카메라 장면에 따라 ACT 평균 출력이 명확히 달라졌다. 특히 J2/J3의 변화가 크고 각 조건 내 표준편차는 작았다. 따라서 **시각 장면 변화가 정책 출력에 실제 영향을 주고 있음**을 확인했다.

단, 이것만으로 모델이 의미론적으로 “컵” 자체를 검출한다고 단정할 수는 없다. 컵이 없는 장면, 다른 물체, 배경 변화 등의 추가 대조 실험이 필요하다.

## 9. STEP 숫자의 의미

실행 중:

```text
STEP 1430
STEP 1440
STEP 1450
...
```

이 값은 **학습 step도 아니고 저장된 episode의 frame 번호도 아니다.**

현재 실행 프로그램이 control loop를 몇 번 수행했는지를 세는 카운터다.

```text
현재 카메라 + 현재 state
        ↓
ACT action
        ↓
안전 제한
        ↓
OMX 이동
        ↓
새로운 관측
        ↓
다음 control step
```

따라서 작업 완료 조건이 없으면 STEP은 계속 증가한다.

## 10. 컵이 없어도 움직이는 이유

현재 ACT 실행기는 별도의 cup detector가 아니다. RGB 영상이 들어오면 정책은 항상 action을 출력할 수 있다.

```text
카메라 + state
       ↓
      ACT
       ↓
    action
```

따라서 학습 데이터가 대부분 컵이 있는 장면이었다면 컵이 없는 입력은 out-of-distribution일 수 있고, 정책이 의미 없는 행동을 낼 수도 있다.

향후 권장 구조:

```text
Camera
  ↓
Cup / Task condition check
  ├─ 조건 불충족 → STOP
  └─ 조건 충족
        ↓
       ACT
        ↓
       OMX
        ↓
Task completion check
        ↓
      STOP
```

## 11. FPS 기반 실행

임의로 “빠르게” 실행하는 것보다 학습 데이터의 실제 FPS에 맞추는 것이 중요하다. `scripts/omx_act_fps_control.py`는 metadata에서 FPS를 찾아 사용하고, 찾지 못하면 10 FPS의 보수적 fallback을 사용하도록 작성했다.

주의: fallback 10 FPS는 **실제 학습 FPS라고 주장하는 값이 아니다.** 원본 LeRobot dataset의 `meta/info.json` 등을 확보하면 그 값을 우선 사용해야 한다.

## 12. 안전 제한

실제 구동 코드는 다음 제한을 둔다.

```text
ARM_MAX_STEP     = 0.05 rad / control step
GRIPPER_MAX_STEP = 0.02 rad / control step
```

또한 학습 데이터에서 확인된 action min/max 범위 밖의 출력을 clip한다.

실제 로봇 테스트 시에는:

- 작업 공간을 비운다.
- 처음에는 저속/작은 step으로 시작한다.
- `Ctrl+C`로 즉시 정지할 수 있게 한다.
- 학습 분포 밖의 자세에서 무리하게 실행하지 않는다.
- 자동 task-complete/timeout/stop 조건을 추가하는 것이 좋다.

## 13. 오늘의 결론

오늘의 핵심은 “컵 집기를 완성했다”가 아니다.

**Google Colab에서 학습된 ACT 정책을 실제 OMX의 카메라와 관절 상태에 연결하고, 정책 출력이 실제 ROS 2/DYNAMIXEL 로봇 동작으로 이어지는 end-to-end 경로를 확인했다**는 데 의미가 있다.

또한 L/C/R 실험을 통해 동일한 로봇 자세에서 시각 장면 변화에 따라 ACT 출력이 달라짐을 확인했다.

다음 단계는:

1. 원본 dataset FPS 확인
2. NO CUP 대조 실험
3. 컵 존재/작업 시작 gate
4. task completion + timeout 자동 정지
5. 카메라 위치와 초기 자세를 학습 조건에 고정
6. 더 많은 episode 수집 및 재학습
7. 성공률 기반 정량 평가

이다.
