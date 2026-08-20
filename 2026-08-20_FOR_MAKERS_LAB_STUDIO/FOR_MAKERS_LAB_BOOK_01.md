# FOR MAKERS LAB BOOK SERIES

## Chapter 01 --- AI와 로봇을 이야기로 만드는 스튜디오

> **FOR MAKERS LAB STUDIO \| ROBOTICS · AI · VIDEO PRODUCTION**

------------------------------------------------------------------------

## 프롤로그 --- 기술을 만드는 것에서, 이야기를 만드는 것으로

오늘의 작업은 하나의 프로그램을 배우거나 하나의 로봇을 움직이는 것으로
끝나지 않았다.

로봇을 어떻게 움직일 것인가. 카메라는 어떻게 공간을 바라보게 할 것인가.
AI는 그 영상에서 무엇을 찾아낼 것인가. 그리고 이 모든 실험을 어떻게
촬영하고 편집해서 한 편의 이야기로 전달할 것인가.

이 질문들이 하나씩 연결되면서 **FOR MAKERS LAB STUDIO**의 방향이 조금 더
분명해졌다.

이곳은 단순한 촬영 스튜디오가 아니다.\
로봇과 AI를 배우고, 직접 실험하고, 실패하고, 다시 수정하며, 그 모든
과정을 영상과 음악을 통해 기록하는 제작 공간이다.

오늘은 그 시스템을 만들어가는 하루였다.

------------------------------------------------------------------------

# 1. FOR MAKERS LAB STUDIO의 방향

오늘 정리한 스튜디오의 핵심 문구는 다음과 같다.

**FOR MAKERS LAB STUDIO \| ROBOTICS · AI · VIDEO PRODUCTION**

세 가지 영역을 하나의 작업 흐름으로 연결한다.

1.  **ROBOTICS** --- 실제 로봇과 모터를 움직인다.
2.  **AI** --- 카메라와 인공지능으로 물체와 공간을 인식한다.
3.  **VIDEO PRODUCTION** --- 실험 과정을 촬영하고 편집해 콘텐츠로
    만든다.

결국 목표는 기술을 단순히 보여주는 것이 아니라, **기술이 만들어지는 과정
자체를 하나의 이야기로 기록하는 것**이다.

------------------------------------------------------------------------

# 2. OBS Studio --- 실험실을 방송 스튜디오로

오늘 영상 제작의 출발점은 OBS Studio였다.

OBS에서는 다음과 같은 요소를 하나의 화면에 구성할 수 있다.

-   로봇 실험 화면
-   Ubuntu 데스크톱 화면
-   AI/YOLO 인식 화면
-   웹캠
-   마이크
-   고정 타이틀과 자막
-   여러 Scene 전환

중요한 원칙도 하나 정했다.

> **OBS는 촬영에 집중하고, 본격적인 음악·컷·자막 편집은 후반 편집에서
> 한다.**

이렇게 하면 촬영 원본을 최대한 깨끗하게 보존할 수 있고, 이후 음악의
크기나 위치를 자유롭게 조정할 수 있다.

### 같은 카메라를 여러 Scene에서 사용할 때

새로운 카메라 장치를 계속 생성하기보다는 OBS 안에서 **기존 소스를
재사용**한다.

이 방식은 같은 장치를 중복으로 열면서 생길 수 있는 충돌을 줄여준다.

------------------------------------------------------------------------

# 3. OBS가 갑자기 사라졌던 문제

작업 도중 OBS 창을 클릭하면 프로그램이 사라지는 것처럼 보이는 문제가
있었다.

터미널에서 OBS를 실행해 확인하는 과정에서 다음 메시지가 나타났다.

``` text
OBS is already running
```

기존 OBS 프로세스가 남아 있는 상태에서 새로운 OBS를 실행하려 했던
것이다.

프로세스를 확인하고 필요할 때 정리한 뒤 OBS 하나만 실행하는 방식으로
다시 테스트했다.

``` bash
pkill obs
pgrep -a obs
obs
```

문제가 다시 발생한다면 GUI 아이콘으로 실행하기보다 터미널에서 `obs`를
실행해 종료 직전 로그를 확인하는 것이 진단에 도움이 된다.

------------------------------------------------------------------------

# 4. 카메라 --- 2D 영상에서 3D 공간으로

기존 작업에서는 일반 RGB 카메라와 YOLO를 이용해 물체의 화면상 위치를
찾았다.

오늘은 여기서 한 단계 더 나아가 **Orbbec Gemini 335L Depth Camera**를
다시 연결했다.

현재 Ubuntu에서 확인된 카메라 장치는 다음과 같았다.

``` text
Orbbec Gemini 335L
/dev/video0 ~ /dev/video7

Insta360 Link 2 Pro
/dev/video8
/dev/video9

HD Pro Webcam C920
/dev/video10
/dev/video11
```

장치 확인 명령:

``` bash
v4l2-ctl --list-devices
```

이 과정에서 중요한 사실을 다시 확인했다.

> Linux에서는 USB 카메라의 `/dev/videoN` 번호가 항상 고정되어 있다고
> 가정하면 안 된다.

따라서 프로그램 실행 전 실제 장치 번호를 확인하는 습관이 중요하다.

------------------------------------------------------------------------

# 5. P1 · P2 · P3 · P4 --- 카메라와 현실 공간 연결하기

오늘 다시 이어가려 했던 핵심 실험은 **P1, P2, P3, P4 캘리브레이션**이다.

카메라 화면에 네 개의 기준점을 지정하고 그 영역을 실제 작업 공간과
대응시킨다.

개념적으로는 다음과 같다.

``` text
P1 ---------------- P2
 |                    |
 |     WORK AREA      |
 |       CENTER       |
 |                    |
P4 ---------------- P3
```

이 네 점은 단순한 화면 표시가 아니다.

카메라가 바라보는 **픽셀 좌표계**와 로봇이 움직이는 **실제 공간
좌표계**를 연결하기 위한 기준이다.

작업 흐름은 다음 방향으로 발전한다.

``` text
Depth Camera
     ↓
RGB / Depth Image
     ↓
YOLO Object Detection
     ↓
Object Center (u, v)
     ↓
P1 · P2 · P3 · P4 Calibration
     ↓
Real-world X · Y
     ↓
Depth Z
     ↓
Robot Coordinate X · Y · Z
     ↓
Robot Arm Motion
```

------------------------------------------------------------------------

# 6. 기존 Orbbec 작업 환경 찾기

처음에는 기존 Insta360용 Python 가상환경에서 Orbbec SDK를 실행하려 했다.

그 결과:

``` text
ModuleNotFoundError: No module named 'pyorbbecsdk'
```

새로 설치하기 전에 기존 환경을 검색했다.

``` bash
find ~/Robotics ~ -type d -path "*/site-packages/pyorbbecsdk" 2>/dev/null | head -20
```

기존 Orbbec 환경을 발견했다.

``` text
/home/formakers/Robotics/orbbec_test/venv
```

작업 폴더:

``` bash
cd ~/Robotics/orbbec_test
```

SDK 확인:

``` bash
python3 -c "import pyorbbecsdk; print('Orbbec SDK OK')"
```

결과:

``` text
Orbbec SDK OK
```

------------------------------------------------------------------------

# 7. 기존 코드 자산

`~/Robotics/orbbec_test`에는 이미 여러 단계의 실험 코드가 남아 있었다.

``` text
depth_only_test.py
gemini_depth_test.py
rgb_distance_test.py
yolo_cup_depth.py
yolo_cup_p1p4_landscape.py
yolo_cup_p1p4.py
yolo_cup_p1p4_vertical.py
yolo_cup_xyz.py
yolo_gemini_xyz.py
```

이 파일들은 단순한 코드 조각이 아니다.

실험이 한 단계씩 발전해온 기록이다.

``` text
Depth 확인
   ↓
RGB + 거리
   ↓
YOLO + Depth
   ↓
P1/P2/P3/P4
   ↓
XYZ 좌표
   ↓
Robot Arm
```

------------------------------------------------------------------------

# 8. Python 환경에서 발견한 문제

`yolo_cup_p1p4_landscape.py`를 실행하면서 다음 오류가 발생했다.

``` text
ModuleNotFoundError: No module named 'ultralytics'
```

또한 가상환경 프롬프트에는 `(venv)`가 표시됐지만 실제 실행 경로를 확인해
보니:

``` bash
which python3
which pip
python3 -m pip --version
```

결과는 시스템 Python을 가리키고 있었다.

``` text
/usr/bin/python3
/usr/bin/pip
```

여기서 얻은 중요한 교훈은 다음과 같다.

> **터미널에 `(venv)`가 보인다는 사실만 믿지 말고, 실제 Python과 pip의
> 경로를 확인한다.**

특히 Ubuntu의 PEP 668 보호 환경에서는 무리하게 시스템 Python에 패키지를
설치하지 않고 프로젝트별 가상환경을 올바르게 사용하는 것이 중요하다.

------------------------------------------------------------------------

# 9. 영상 제작 --- 촬영과 편집의 역할 분리

오늘 영상 제작 시스템은 크게 두 단계로 정리됐다.

## 촬영 --- OBS Studio

``` text
Camera
Robot
Desktop
AI Detection
Webcam
Microphone
       ↓
    OBS Studio
       ↓
 Clean Recording
```

## 후반 작업 --- Kdenlive

``` text
OBS Recording
      ↓
Cut Editing
      ↓
Background Music
      ↓
Voice / Music Balance
      ↓
Titles & Captions
      ↓
Intro / Outro
      ↓
Final Render
```

Kdenlive에서는 유튜브 일반 영상용으로 다음과 같은 기본 구성을 사용했다.

``` text
Resolution : 1920 × 1080
Frame Rate : 30 fps
Container  : MP4
Video      : H.264
Audio      : AAC
```

렌더 프리셋:

``` text
MP4-H264/AAC
```

------------------------------------------------------------------------

# 10. 목소리와 음악

영상에서 가장 중요한 소리는 배경음악이 아니라 **사람의 목소리**다.

OBS에서 말하는 목소리는 대략 다음 범위를 기준으로 잡을 수 있다.

``` text
Normal voice     : -18 ~ -12 dB
Strong emphasis  : -10 ~  -6 dB
Avoid            : 0 dB clipping
```

배경음악은 목소리를 가리지 않는 수준에서 시작하고, 편집 과정에서 장면에
맞춰 조절한다.

로봇이 움직이는 장면에서는 음악을 조금 살리고, 설명이 중요한 부분에서는
음악을 낮춘다.

음악도 결국 기술 설명을 방해하는 요소가 아니라 **이야기의 감정을
전달하는 또 하나의 도구**가 된다.

------------------------------------------------------------------------

# 11. 오늘 만들어진 하나의 시스템

오늘 한 작업들을 멀리서 바라보면 각각 다른 프로그램을 공부한 것처럼
보인다.

하지만 실제로는 하나의 파이프라인으로 연결된다.

``` text
REAL WORLD
    ↓
DEPTH CAMERA
    ↓
AI / YOLO
    ↓
COORDINATE MAPPING
    ↓
ROBOTICS
    ↓
OBS RECORDING
    ↓
KDENLIVE EDITING
    ↓
MUSIC + NARRATION
    ↓
YOUTUBE
```

그리고 이것이 앞으로 **FOR MAKERS LAB STUDIO**가 발전시켜 갈 하나의 제작
방식이다.

------------------------------------------------------------------------

# 12. 실패도 기록한다

오늘도 여러 오류가 있었다.

카메라가 열리지 않았다.

가상환경이 예상대로 동작하지 않았다.

Python 패키지가 없었다.

OBS가 이상하게 동작했다.

하지만 이런 순간들이 작업의 실패라고 생각하지 않는다.

오히려 실제 시스템을 만드는 과정에서는 **왜 작동하지 않았는지를 찾아가는
과정 자체가 기술**이다.

``` text
문제 발견
   ↓
원인 확인
   ↓
한 단계 테스트
   ↓
수정
   ↓
다시 실행
   ↓
기록
```

이 반복이 쌓이면 어느 순간 단순히 프로그램을 사용하는 사람이 아니라
**자신의 시스템을 만들어가는 사람**이 된다.

------------------------------------------------------------------------

# 에필로그 --- 오늘도 하나를 연결했다

처음부터 모든 것을 알고 시작할 필요는 없다.

궁금한 것을 하나씩 질문하고, 직접 실행하고, 실패하면 다시 확인한다.

카메라 하나를 연결하는 일이 AI로 이어지고, AI는 로봇으로 이어지고,
로봇의 움직임은 다시 영상이 된다.

그리고 영상에는 목소리와 음악이 들어가면서 하나의 이야기가 된다.

**FOR MAKERS LAB STUDIO는 완성된 공간이 아니다.**

계속 만들어지고 있는 공간이다.

오늘보다 내일 하나 더 연결하고,\
어제보다 오늘 하나 더 이해하면서,\
AI와 로봇이 현실에서 만나는 순간들을 직접 기록한다.

> **기술을 배우는 것에서 끝나지 않는다.\
> 기술을 연결하고, 그 과정을 이야기로 만든다.**

**FOR MAKERS LAB STUDIO**\
**ROBOTICS · AI · VIDEO PRODUCTION**

------------------------------------------------------------------------

## Next Chapter

다음 장에서는 다음 연결을 완성한다.

**Orbbec Gemini 335L → YOLO → P1/P2/P3/P4 → XYZ → Robot Arm**

카메라가 바라본 하나의 점이 실제 로봇의 움직임이 되는 순간을 기록한다.

------------------------------------------------------------------------

*FOR MAKERS LAB BOOK SERIES --- Chapter 01*\
*2026-08-20*
