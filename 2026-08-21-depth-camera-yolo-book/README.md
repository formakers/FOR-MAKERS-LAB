# 3D Depth Camera + YOLO 실전 입문

> 바이브 코딩으로 컵 인식부터 거리·크기·3D 위치 측정까지\
> FOR MAKERS LAB · 2026-08-21

오늘의 실험은 단순한 질문에서 시작했습니다.

**"3D Depth 카메라로 컵을 인식하고, 컵 주위에 박스를 그린 뒤 거리와 실제
크기까지 표시할 수 있을까?"**

이 저장소는 그 질문을 실제 하드웨어 실험으로 확인한 과정을 초보자도 다시
따라갈 수 있도록 정리한 실습 노트입니다.

## 오늘 구현한 흐름

`RGB 영상 → YOLO 컵 인식 → 2D Bounding Box → Depth 측정 → X·Y·Z 위치 → 실제 크기(cm) → 3D Box 시각화`

## 핵심 결과

-   RGB 실시간 영상 입력
-   YOLO로 `CUP` 자동 인식
-   Confidence 표시
-   컵 중심 픽셀 표시
-   Depth를 이용한 거리(Z) 측정
-   X·Y·Z 3차원 위치 계산
-   Width·Height를 cm 단위로 추정
-   3D Bounding Box 형태로 시각화
-   OBS에서 Python 결과 화면 캡처
-   AI와 대화하며 기능을 반복 개선하는 바이브 코딩 실습

## 파일

-   `BOOK.md` --- 전체 실습 책
-   `README.md` --- GitHub 첫 화면
-   `requirements-example.txt` --- 사용 라이브러리 예시

## 중요한 주의

이 저장소의 책은 **2026-08-21 실제 실험의 개념·작업 흐름을 정리한
기록**입니다.\
Depth SDK의 실제 API와 스트림 프로파일은 사용하는 카메라 모델/펌웨어에
따라 달라질 수 있습니다. 실행 코드는 반드시 현재 장비에서 검증한 원본
Python 파일을 함께 보관하는 것을 권장합니다.

------------------------------------------------------------------------

**FOR MAKERS LAB**\
AI · Robotics · Computer Vision · Physical AI · Vibe Coding
