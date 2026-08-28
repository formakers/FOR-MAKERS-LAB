# Depth Camera + ROBOTIS OMX 로봇팔 자동 Pick & Place

Depth Camera, YOLO, 3D 좌표 계산, 카메라-로봇 좌표 변환, OMX 로봇팔 제어, Pick & Place까지 전체 데이터 흐름을 정리한 교육용 프로젝트입니다.

## 핵심 흐름

```text
Depth Camera
   ↓
YOLO 객체 검출
   ↓
2D Pixel + Depth
   ↓
Camera XYZ
   ↓
Robot XYZ
   ↓
IK + ROS 2 Control
   ↓
Pick & Place
```

## 문서

- [전체 책 보기](BOOK.md)
- [프로젝트 파일 안내](PROJECT_FILES.md)

## 권장 이미지 구조

```text
images/
├── 01-overview.png
├── 02-depth-camera.png
├── 03-yolo-detection.png
├── 04-3d-coordinate.png
├── 05-coordinate-transform.png
├── 06-omx-control.png
└── 07-pick-place.png
```

## 주요 키워드

ROBOTIS OMX, ROS 2, Depth Camera, RGB-D, YOLO, 3D Vision, Camera Calibration, TF2, Inverse Kinematics, Pick and Place, Physical AI
