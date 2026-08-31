# OMX-F Pick & Place System Design Book

OMX-F 매니퓰레이터와 Depth Camera를 이용한 Pick & Place 시스템의
전체 구조를 학습하기 위한 설계도 및 설명 자료입니다.

## 구성

- `OMX-F_Pick_and_Place_System_Book.docx`
  - 전체 시스템 흐름
  - 좌표계 구성
  - OMX-F 사양 및 좌표
  - Pick & Place 시퀀스
  - ROS 2 Topic / Action
  - 개발 및 실험 순서
  - 주요 파라미터와 주의사항

- `images/`
  - 00-overview.png : 전체 시스템 설계도
  - 01-system-architecture.png : 전체 시스템 구성 상세도
  - 02-coordinate-system.png : 좌표계 구성 상세도
  - 03-omx-f-spec-coordinate.png : OMX-F 사양 및 좌표 상세도
  - 04-pick-place-sequence.png : Pick & Place 시퀀스 상세도
  - 05-ros2-topics-actions.png : ROS 2 토픽 및 액션 상세도
  - 06-development-experiment-flow.png : 개발 및 실험 순서 상세도
  - 07-key-parameters.png : 주요 파라미터 상세도

## 전체 흐름

Depth Camera → YOLO 객체 인식 → 3D 좌표 계산 →
Camera-to-Robot 좌표 변환 → MoveIt 2 경로 계획 →
OMX-F 제어 → Gripper Pick & Place

## 주의

본 자료의 일부 파라미터와 수치는 시스템 구조를 이해하기 위한
개념 및 예시값이 포함되어 있습니다. 실제 장비 적용 시에는
URDF, camera_info, TF, 캘리브레이션, MoveIt 2 설정 및
실제 로봇의 동작 범위를 직접 확인하고 검증해야 합니다.
