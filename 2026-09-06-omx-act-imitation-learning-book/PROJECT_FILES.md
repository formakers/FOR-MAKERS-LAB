# PROJECT_FILES

```text
2026-09-06-omx-act-imitation-learning-book/
├── README.md
├── BOOK.md
├── PROJECT_FILES.md
├── images/
│   └── 01-omx-act-system-design.png
├── scripts/
│   ├── omx_act_cup_test.py
│   └── omx_act_fps_control.py
└── pretrained_model/
    └── README.md
```

## 파일 역할

- `README.md` — 프로젝트 개요와 빠른 실행
- `BOOK.md` — 2026-09-06 실제 실험 과정, 명령어, 결과와 해석
- `images/01-omx-act-system-design.png` — 전체 시스템 설계도
- `scripts/omx_act_cup_test.py` — 로봇을 움직이지 않고 Left/Center/Right 장면의 ACT 출력을 비교
- `scripts/omx_act_fps_control.py` — ACT 출력을 ROS 2 ARM/Gripper 제어로 연결하는 closed-loop 실행 예제
- `pretrained_model/README.md` — 학습 모델 파일 배치 안내

## 주의

실제 하드웨어 구성, LeRobot 버전, 컨트롤러 설정에 따라 토픽/액션/QoS/관절 제한은 달라질 수 있습니다. 실제 구동 전에는 저속·소범위 테스트를 권장합니다.
