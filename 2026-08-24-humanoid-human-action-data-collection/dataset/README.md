# Dataset Notes

## 기본 구조

```text
dataset/
├── episode_0001/
│   ├── sensor_data.csv
│   ├── rgb/
│   ├── depth/
│   └── label.json
└── ...
```

## 권장 필드

```text
timestamp
finger[5]
wrist_imu
hand_pos[x,y,z]
object_class
object_pos[x,y,z]
rgb_path
depth_path
robot_joint[n]
```

## Episode 예시

```text
pick_and_place_cup
```

- 손 접근
- 손 열기
- 컵 접촉
- 손가락 닫기
- 들어 올리기
- 이동
- 내려놓기
- 손 열기
