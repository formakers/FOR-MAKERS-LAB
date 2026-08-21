# FOR MAKERS LAB 실전 제작 노트

## AI · OBS Studio · Background Removal · GitHub로 만드는 AI 제작 스튜디오

**작성일: 2026-08-21**

---

# 들어가며

오늘의 작업은 단순히 OBS Studio의 몇 가지 기능을 테스트한 것이 아니다.

우리는 하나의 제작 시스템을 만들어가고 있다.

사람이 아이디어를 말한다.

ChatGPT와 대화한다.

필요한 프로그램과 기능을 찾는다.

직접 설치한다.

화면을 구성한다.

문제가 발생한다.

원인을 찾는다.

다시 수정한다.

완성된 작업을 영상으로 기록한다.

그리고 마지막에는 GitHub에 기술 문서로 남긴다.

전체 구조는 다음과 같다.

```text
아이디어
   ↓
ChatGPT와 대화
   ↓
설치 / 설정 / 코드
   ↓
Ubuntu에서 실행
   ↓
OBS Studio 화면 구성
   ↓
AI / Robot / Camera 연결
   ↓
테스트
   ↓
문제 발견
   ↓
수정
   ↓
영상 녹화
   ↓
편집
   ↓
YouTube
   ↓
GitHub 문서화
```

이 책의 핵심은 특정 프로그램 하나를 배우는 것이 아니다.

**여러 기술을 연결해서 실제로 작동하는 제작 시스템을 만드는 방법**을 기록하는 것이다.

---

# PART 1. 오늘 무엇을 만들었는가

## 1. FOR MAKERS LAB 제작 스튜디오

오늘 구성한 환경은 일반적인 OBS 방송 화면보다 조금 더 넓은 개념이다.

OBS Studio를 중심으로 다음 요소를 연결한다.

```text
웹캠
컴퓨터 화면
ChatGPT
AI Visualizer
로봇 카메라
YOLO 화면
Depth Camera
상태 표시
텍스트
이미지
배경음악
마이크
```

OBS는 이 모든 것을 하나의 화면으로 합쳐준다.

따라서 OBS는 단순한 녹화 프로그램이 아니라

**FOR MAKERS LAB의 영상 제작 허브**

역할을 하게 된다.

---

# PART 2. OBS Studio 이해하기

# 2. Scene이란 무엇인가

OBS에서 Scene은 하나의 완성된 화면이다.

예를 들어 다음처럼 만들 수 있다.

```text
Scene 01 : FOR MAKERS LAB 인트로
Scene 02 : 로봇 전체 화면
Scene 03 : AI 인식 화면
Scene 04 : ChatGPT 설명 화면
Scene 05 : 웹캠 + 로봇
Scene 06 : YOLO Target Tracking
Scene 07 : Depth Camera
Scene 08 : 마무리 화면
```

영상 촬영 중 Scene을 전환하면 실제 방송 스튜디오처럼 사용할 수 있다.

---

# 3. Source란 무엇인가

Scene 안에 들어가는 각각의 요소가 Source다.

대표적인 Source는 다음과 같다.

```text
Video Capture Device
Display Capture
Window Capture
Image
Media Source
Text
Color Source
Browser Source
Audio Input Capture
Audio Output Capture
```

예를 들어 하나의 Scene은 다음과 같이 구성할 수 있다.

```text
AI ROBOT SCENE
│
├── Background
├── Robot Camera
├── ChatGPT Window
├── AI Visualizer
├── Webcam
├── Title
├── Status Text
└── Microphone
```

---

# PART 3. Ubuntu에 OBS Studio 설치하기

## 4. 먼저 현재 설치 상태 확인

터미널을 연다.

```bash
obs --version
```

정상적으로 설치되어 있다면 OBS 버전이 표시된다.

설치 위치 확인:

```bash
which obs
```

패키지 확인:

```bash
apt list --installed 2>/dev/null | grep obs
```

Flatpak으로 설치했는지 확인:

```bash
flatpak list | grep -i obs
```

이 확인이 중요한 이유가 있다.

Background Removal 플러그인은 OBS가

```text
APT / PPA 설치인지
Flatpak 설치인지
```

에 따라 설치 방법이 달라지기 때문이다.

---

# 5. Ubuntu에서 OBS 설치 — 공식 PPA 방식

먼저 패키지 정보를 갱신한다.

```bash
sudo apt update
```

PPA 관리 도구가 없다면 설치한다.

```bash
sudo apt install software-properties-common
```

OBS 공식 PPA 추가:

```bash
sudo add-apt-repository ppa:obsproject/obs-studio
```

패키지 목록 갱신:

```bash
sudo apt update
```

OBS 설치:

```bash
sudo apt install obs-studio
```

실행:

```bash
obs
```

버전 확인:

```bash
obs --version
```

---

# 6. Flatpak 방식 OBS 설치

Flatpak이 필요한 경우:

```bash
sudo apt update
```

```bash
sudo apt install flatpak
```

Flathub 추가:

```bash
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

OBS 설치:

```bash
flatpak install flathub com.obsproject.Studio
```

OBS 실행:

```bash
flatpak run com.obsproject.Studio
```

---

# PART 4. Background Removal

# 7. Background Removal이란 무엇인가

일반적인 웹캠은 다음과 같이 촬영한다.

```text
사람 + 방 + 책상 + 벽 + 뒤쪽 물건
```

우리가 원하는 것은 다음과 같다.

```text
사람만 남김
```

AI Background Removal은 카메라 영상에서 사람을 분석하고 사람과 배경 사이의 마스크를 생성한다.

개념적으로는 다음과 같다.

```text
Camera Frame
      ↓
AI Segmentation
      ↓
Person Mask
      ↓
Background 제거
      ↓
투명한 인물 영상
```

이 투명 영상을 로봇 화면이나 ChatGPT 화면 위에 올릴 수 있다.

---

# 8. Background Removal과 크로마키 차이

크로마키는 일반적으로 녹색 배경을 사용한다.

```text
Green Screen
     ↓
특정 색 제거
     ↓
사람만 표시
```

Background Removal은 다르다.

```text
일반 방
     ↓
AI 사람 인식
     ↓
사람과 배경 분리
```

따라서 그린스크린을 설치하지 않아도 된다.

---

# 9. Luma Key와의 차이

Luma Key는 밝기를 기준으로 제거한다.

예를 들어 검은색 배경의 그래픽이 있다고 하자.

```text
검은색 배경
+
밝은 그래픽
```

Luma Key를 적용하면 어두운 부분을 투명하게 만들 수 있다.

하지만 사람의 몸과 방 배경처럼 복잡한 영상에서는 Background Removal이 더 적합하다.

---

# PART 5. Background Removal 설치

# 10. 가장 중요한 원칙

OBS 설치 방식과 Background Removal 설치 방식을 맞추는 것이 중요하다.

```text
OBS PPA 설치
→ Background Removal DEB

OBS Flatpak 설치
→ Background Removal Flatpak
```

서로 다른 방식을 섞으면 플러그인이 OBS에서 나타나지 않을 가능성이 있다.

---

# 11. Flatpak OBS일 때

가장 간단하다.

```bash
flatpak install flathub com.obsproject.Studio.Plugin.BackgroundRemoval
```

설치 후 OBS를 완전히 종료한다.

다시 실행한다.

```bash
flatpak run com.obsproject.Studio
```

---

# 12. PPA OBS일 때 Background Removal 설치

GitHub의 Background Removal Release에서 Ubuntu용 `.deb` 파일을 받는다.

다운로드 폴더로 이동한다.

```bash
cd ~/Downloads
```

파일 확인:

```bash
ls
```

예를 들어 파일 이름이 다음과 비슷하게 보일 수 있다.

```text
obs-backgroundremoval-xxxxx-linux-gnu.deb
```

설치:

```bash
sudo dpkg -i ./obs-backgroundremoval*.deb
```

의존성 문제가 발생한다면:

```bash
sudo apt-get install -f
```

다시 설치:

```bash
sudo dpkg -i ./obs-backgroundremoval*.deb
```

OBS를 종료했다가 다시 시작한다.

```bash
obs
```

---

# 13. 플러그인이 설치됐는지 확인

OBS를 실행한다.

웹캠 Source를 선택한다.

마우스 오른쪽 버튼:

```text
Filters
```

로 들어간다.

Effect Filters에서 `+`를 누른다.

Background Removal 관련 필터가 나타나면 설치가 성공한 것이다.

---

# PART 6. 웹캠 추가

# 14. Video Capture Device 추가

OBS 아래쪽 Sources 영역에서:

```text
+
```

를 누른다.

다음 메뉴 선택:

```text
Video Capture Device
```

새 Source 이름 예:

```text
FOR MAKERS Webcam
```

장치를 선택한다.

예:

```text
Logitech C920
Insta360 Link 2 Pro
```

해상도도 확인한다.

일반적인 유튜브 영상에서는:

```text
1920 × 1080
```

또는

```text
1280 × 720
```

을 사용할 수 있다.

---

# PART 7. Background Removal 필터 적용

# 15. 웹캠 Source 선택

Sources에서:

```text
FOR MAKERS Webcam
```

선택.

마우스 오른쪽:

```text
Filters
```

선택.

Effect Filters의 `+` 클릭.

Background Removal 추가.

---

# 16. 기본 튜닝

AI 배경 제거에서 중요한 것은 단순히 필터를 켜는 것만이 아니다.

일반적으로 다음 요소를 조정하게 된다.

```text
Threshold
Smoothing
Feathering
Model
Blur
Edge 처리
```

머리카락 주변이 잘리는 경우에는 경계 설정을 너무 강하게 하지 않는 것이 좋다.

반대로 방 배경 일부가 같이 남는다면 Threshold를 조금 강하게 조정한다.

---

# 17. 조명의 중요성

AI Background Removal도 카메라 영상이 좋을수록 정확하다.

좋은 조건:

```text
얼굴 앞쪽 조명
인물과 배경의 밝기 차이
복잡하지 않은 배경
카메라 노이즈가 적은 환경
```

나쁜 조건:

```text
역광
너무 어두운 방
배경과 옷 색상이 거의 같음
빠른 움직임
심한 카메라 노이즈
```

즉 Background Removal 성능을 높이기 위해서는 AI 모델뿐 아니라 **촬영 환경 자체를 개선하는 것**도 중요하다.

---

# PART 8. 웹캠 화면 위치 조정

# 18. 화면 크기

사람이 화면의 절반을 차지하면 로봇이나 AI 화면이 잘 보이지 않는다.

따라서 보조 설명 화면에서는 웹캠을 작게 배치할 수 있다.

예:

```text
┌─────────────────────────────┐
│                             │
│       ROBOT / AI            │
│                             │
│                    ┌──────┐ │
│                    │PERSON│ │
│                    └──────┘ │
└─────────────────────────────┘
```

---

# 19. Crop 사용

OBS에서 Source를 선택한다.

`Alt` 키를 누른 상태에서 Source 가장자리를 드래그한다.

그러면 화면 자체의 크기가 줄어드는 것이 아니라 불필요한 영역이 잘린다.

이 기능은 매우 중요하다.

예:

```text
ChatGPT 전체 브라우저
```

에서

```text
대화 영역만
```

남길 수 있다.

---

# PART 9. 화면 디자인

# 20. Color Source

Sources:

```text
+
→ Color Source
```

를 선택한다.

여기서 배경색을 만들 수 있다.

AI·로봇 영상에는 다음 계열이 잘 어울린다.

```text
검정
Dark Gray
Navy
Deep Blue
```

중요 상태 정보에는:

```text
Yellow
Blue
Red
```

같은 색을 사용할 수 있다.

---

# 21. Text Source

Sources:

```text
+
→ Text
```

예:

```text
FOR MAKERS LAB
```

또는

```text
AI TARGET TRACKING
```

또는

```text
BACKGROUND REMOVAL
```

영상 자막은 너무 길지 않은 것이 좋다.

---

# 22. 글씨 크기

OBS 편집 화면에서 읽히는 글씨도 스마트폰에서는 매우 작을 수 있다.

따라서 일반 문서보다 훨씬 큰 폰트가 필요하다.

중요한 것은

**예쁘게 만드는 것보다 읽히게 만드는 것**

이다.

---

# PART 10. AI Visualizer

# 23. AI 화면을 별도의 Source로 만들기

AI Visualizer가 독립된 프로그램이나 Browser 화면이라면 Window Capture 또는 Browser Source로 가져올 수 있다.

예:

```text
AI Visualizer
+
ChatGPT
+
Robot Camera
+
Webcam
```

화면 구성:

```text
┌──────────────────────────────────┐
│ FOR MAKERS LAB                   │
│                                  │
│   AI VISUALIZER   ROBOT CAMERA   │
│                                  │
│   ChatGPT         PERSON         │
│                                  │
│ AI TARGET : LOCK                 │
└──────────────────────────────────┘
```

이렇게 하면 일반적인 화면 녹화가 아니라 하나의 프로그램 같은 영상이 된다.

---

# PART 11. Scene 복제와 버전 관리

# 24. Scene을 바로 수정하지 말아야 하는 이유

화면이 잘 만들어졌는데 새로운 디자인을 시험하다가 망가질 수 있다.

따라서 복제한다.

예:

```text
Robot Full
```

복제:

```text
Robot Full V2
```

또 다시 실험:

```text
Robot Full V3
```

이것은 프로그래밍의 버전 관리와 매우 비슷하다.

---

# 25. OBS 내부에서도 버전 관리 사고방식을 사용하자

```text
Scene V1
Scene V2
Scene V3
```

처럼 만들어 놓으면 문제가 발생했을 때 이전 화면으로 돌아갈 수 있다.

Git의 commit과 비슷한 사고방식이다.

---

# PART 12. 노이즈와 오디오

# 26. 영상 품질에서 소리가 중요한 이유

시청자는 영상 화질이 조금 낮아도 볼 수 있다.

하지만 지속적인 잡음이 심하면 영상을 보기 어렵다.

따라서 다음을 점검한다.

```text
마이크 입력
Desktop Audio
배경음악
Robot Sound
AI Sound Effect
```

---

# 27. Noise Suppression

마이크 Source:

```text
Filters
```

에서 Noise Suppression 필터를 사용할 수 있다.

환경에 따라:

```text
RNNoise
Speex
```

등의 노이즈 억제 방법을 사용할 수 있다.

노이즈 제거를 너무 강하게 적용하면 목소리가 로봇처럼 변할 수 있으므로 적당히 조절한다.

---

# 28. 배경음악

음악은 메인 콘텐츠보다 작아야 한다.

말을 할 때 음악 때문에 목소리가 묻히면 안 된다.

전체 구조는 다음과 같이 생각하면 좋다.

```text
Voice       = Main
Robot Sound = Effect
Music       = Background
```

---

# PART 13. 오늘 작업의 핵심 스킬

# 29. Skill 1 — 화면 설계

단순히 Source를 넣는 것이 아니라

**무엇을 크게 보여줄 것인가**

를 결정하는 능력이다.

중요 화면:

```text
크게
```

보조 화면:

```text
작게
```

불필요한 화면:

```text
Crop
```

---

# 30. Skill 2 — AI 배경 분리

웹캠에서 사람만 분리하여 로봇 화면 위에 배치할 수 있게 되었다.

이 기술은 앞으로 다음에 활용할 수 있다.

```text
로봇 설명 영상
강의
튜토리얼
YouTube
Live Streaming
제품 소개
AI 데모
```

---

# 31. Skill 3 — Scene Switching

여러 Scene을 미리 만들어 촬영 중 전환하면 후편집 작업을 크게 줄일 수 있다.

즉 OBS에서 어느 정도의

**실시간 편집**

을 수행하게 된다.

---

# 32. Skill 4 — AI와 대화하면서 시스템 만들기

오늘 가장 중요한 스킬이다.

명령어를 전부 외우지 않아도 된다.

목표를 설명한다.

```text
"웹캠 배경을 없애고 싶다."
```

AI가 방법을 제시한다.

실행한다.

문제가 생긴다.

다시 결과를 알려준다.

```text
"필터가 안 보여."
```

다시 해결한다.

이러한 반복 작업 자체가 AI 시대의 새로운 제작 방식이다.

---

# 33. Skill 5 — 실패 로그 읽기

문제가 발생하면 감으로 해결하기보다 로그를 본다.

예:

```bash
obs --version
```

```bash
flatpak list
```

```bash
apt list --installed | grep obs
```

```bash
which obs
```

문제가 생겼을 때 현재 상태를 먼저 확인하는 습관이 중요하다.

---

# PART 14. GitHub 기록 시스템

# 34. 왜 GitHub에 올리는가

영상은 결과를 보여준다.

하지만 영상에서 명령어를 다시 찾기는 어렵다.

GitHub는 다음을 보관한다.

```text
명령어
설치 과정
코드
설정
실패 기록
해결 방법
스크린샷
문서
```

따라서

```text
YouTube = 보여주기
GitHub  = 다시 따라 하기
```

라는 역할 분담이 가능하다.

---

# PART 15. Git 설치

# 35. Git 설치 확인

```bash
git --version
```

설치되지 않았다면:

```bash
sudo apt update
```

```bash
sudo apt install git
```

확인:

```bash
git --version
```

---

# 36. Git 사용자 정보 설정

이 설정은 Git commit 기록에 사용된다.

```bash
git config --global user.name "FOR MAKERS"
```

이메일 설정:

```bash
git config --global user.email "YOUR_EMAIL@example.com"
```

확인:

```bash
git config --global --list
```

---

# PART 16. 프로젝트 폴더 만들기

오늘 날짜를 넣어서 프로젝트를 관리할 수 있다.

```bash
mkdir -p ~/FOR-MAKERS-LAB/2026-08-21-ai-obs-studio
```

폴더 이동:

```bash
cd ~/FOR-MAKERS-LAB/2026-08-21-ai-obs-studio
```

현재 위치 확인:

```bash
pwd
```

---

# 37. 기본 폴더 구조

```bash
mkdir -p docs images scripts videos examples
```

확인:

```bash
tree
```

`tree`가 없다면:

```bash
sudo apt install tree
```

다시 실행:

```bash
tree
```

구조:

```text
2026-08-21-ai-obs-studio/
│
├── README.md
├── docs/
├── images/
├── scripts/
├── videos/
└── examples/
```

---

# PART 17. README 만들기

# 38. 터미널에서 README 생성

```bash
touch README.md
```

편집:

```bash
nano README.md
```

이 책의 내용을 붙여 넣는다.

Nano 저장:

```text
Ctrl + O
```

Enter.

종료:

```text
Ctrl + X
```

파일 확인:

```bash
cat README.md
```

---

# PART 18. Git 시작

# 39. 저장소 초기화

프로젝트 폴더 안에서:

```bash
git init
```

현재 상태:

```bash
git status
```

이 순간 `.git`이라는 숨김 폴더가 만들어진다.

확인:

```bash
ls -la
```

`.git`은 프로젝트의 변경 기록을 관리한다.

절대 일반 폴더처럼 함부로 삭제하지 않는다.

---

# 40. 파일 Stage

전체 파일 추가:

```bash
git add .
```

상태 확인:

```bash
git status
```

---

# 41. 첫 Commit

```bash
git commit -m "Initial FOR MAKERS LAB OBS Studio book"
```

Commit은 현재 프로젝트 상태의 스냅샷이라고 생각하면 된다.

---

# PART 19. GitHub 연결

# 42. GitHub에서 Repository 생성

GitHub에서 새로운 Repository를 만든다.

예:

```text
for-makers-ai-obs-studio
```

가능하면 처음 연결할 때 README 자동 생성 옵션을 끄고 빈 Repository를 만들면 로컬 프로젝트와 연결하기 편하다.

---

# 43. Branch 이름 main으로 설정

```bash
git branch -M main
```

---

# 44. Remote 연결

GitHub Repository 주소가 예를 들어 다음이라면:

```text
https://github.com/USERNAME/for-makers-ai-obs-studio.git
```

터미널:

```bash
git remote add origin https://github.com/USERNAME/for-makers-ai-obs-studio.git
```

확인:

```bash
git remote -v
```

---

# 45. GitHub로 첫 Push

```bash
git push -u origin main
```

정상적으로 완료되면 GitHub 웹사이트에서 파일이 나타난다.

---

# PART 20. 이후 수정 작업

# 46. 파일 수정

README 수정:

```bash
nano README.md
```

수정 후:

```bash
git status
```

---

# 47. 변경 사항 추가

```bash
git add .
```

---

# 48. Commit

```bash
git commit -m "Update OBS background removal guide"
```

---

# 49. GitHub 업로드

```bash
git push
```

앞으로 가장 많이 사용하는 패턴은 이것이다.

```bash
git status
git add .
git commit -m "작업 내용"
git push
```

---

# PART 21. Git의 의미

# 50. git status

```bash
git status
```

현재 어떤 파일이 변경됐는지 확인한다.

---

# 51. git add

```bash
git add .
```

다음 기록에 포함할 파일을 선택한다.

---

# 52. git commit

```bash
git commit -m "설명"
```

현재 상태를 하나의 기록으로 저장한다.

---

# 53. git push

```bash
git push
```

로컬 컴퓨터의 Git 기록을 GitHub 서버로 보낸다.

---

# 54. git pull

다른 곳에서 GitHub 내용이 변경된 경우:

```bash
git pull
```

GitHub 변경 내용을 현재 컴퓨터로 가져온다.

---

# 55. git log

작업 기록 확인:

```bash
git log --oneline
```

예:

```text
a12345 Update background removal
b67291 Add OBS guide
c83210 Initial commit
```

---

# PART 22. GitHub용 추천 구조

```text
FOR-MAKERS-LAB/
│
├── README.md
│
├── docs/
│   ├── 01-obs-install.md
│   ├── 02-background-removal.md
│   ├── 03-scene-design.md
│   ├── 04-ai-visualizer.md
│   ├── 05-audio-noise.md
│   ├── 06-github-workflow.md
│   └── 07-troubleshooting.md
│
├── scripts/
│
├── images/
│   ├── obs-main.png
│   ├── background-removal.png
│   └── studio-layout.png
│
├── examples/
│
└── CHANGELOG.md
```

---

# PART 23. 날짜별 기록

프로젝트가 계속 커지면 날짜를 기록하는 것이 좋다.

예:

```text
docs/log/
├── 2026-08-17.md
├── 2026-08-18.md
├── 2026-08-19.md
├── 2026-08-20.md
└── 2026-08-21.md
```

그러면 나중에

**어떤 날 무엇을 했는지**

확인할 수 있다.

---

# PART 24. 문제 해결 방법

# 56. OBS에서 Background Removal이 안 보이는 경우

먼저 OBS 설치 방식을 확인한다.

```bash
which obs
```

그리고:

```bash
flatpak list | grep -i obs
```

APT 확인:

```bash
apt list --installed 2>/dev/null | grep obs
```

OBS는 PPA인데 플러그인은 Flatpak으로 설치했거나 그 반대라면 서로 인식하지 못할 수 있다.

---

# 57. 카메라가 안 나오는 경우

카메라 장치 확인:

```bash
v4l2-ctl --list-devices
```

명령어가 없다면:

```bash
sudo apt install v4l-utils
```

다시:

```bash
v4l2-ctl --list-devices
```

Video device 확인:

```bash
ls -l /dev/video*
```

---

# 58. 카메라가 다른 프로그램에서 사용 중인 경우

OBS, Python, 브라우저, 카메라 테스트 프로그램 등이 동일한 카메라를 동시에 점유할 수 있다.

어떤 프로그램이 사용하는지 확인:

```bash
fuser /dev/video0
```

더 자세히:

```bash
sudo lsof /dev/video0
```

---

# PART 25. OBS 업그레이드 방법

# 59. PPA OBS 업그레이드

업데이트 정보 갱신:

```bash
sudo apt update
```

업그레이드:

```bash
sudo apt upgrade
```

OBS만 업그레이드:

```bash
sudo apt install --only-upgrade obs-studio
```

버전 확인:

```bash
obs --version
```

---

# 60. Flatpak OBS 업그레이드

```bash
flatpak update com.obsproject.Studio
```

전체 Flatpak 업데이트:

```bash
flatpak update
```

---

# 61. Background Removal Flatpak 업그레이드

```bash
flatpak update com.obsproject.Studio.Plugin.BackgroundRemoval
```

---

# 62. 업그레이드 전에 해야 할 일

OBS Scene과 Profile이 중요하다면 무조건 백업하는 습관을 갖는 것이 좋다.

특히 플러그인이나 OBS의 큰 버전을 올릴 때는 현재 작업 환경을 보존한다.

원칙:

```text
현재 정상 작동 확인
      ↓
백업
      ↓
OBS 업데이트
      ↓
플러그인 업데이트
      ↓
테스트
      ↓
정상 확인
```

한꺼번에 모든 것을 변경하면 문제가 발생했을 때 원인을 찾기 어렵다.

---

# PART 26. 앞으로의 업그레이드 방향

# 63. LEVEL 1 — 현재 단계

현재 시스템:

```text
OBS
+
Webcam
+
Background Removal
+
ChatGPT
+
AI Visualizer
+
Robot Screen
```

이 상태만으로도 좋은 기술 영상 제작이 가능하다.

---

# 64. LEVEL 2 — 오디오 개선

추가:

```text
Noise Suppression
Compressor
Limiter
Background Music
Fade In
Fade Out
```

목표:

```text
깨끗한 음성
자연스러운 배경음악
일관된 볼륨
```

---

# 65. LEVEL 3 — 로봇 실시간 상태 표시

ROS 또는 Python 프로그램의 데이터를 OBS 화면에 표시한다.

예:

```text
ROBOT : ONLINE
TARGET : LOCK
DISTANCE : 684 mm
MOTOR 1 : 2048
AI : ACTIVE
```

이 단계부터 OBS 화면이 단순 영상이 아니라 실제 로봇 HUD처럼 보이기 시작한다.

---

# 66. LEVEL 4 — YOLO 연동

카메라:

```text
Camera
   ↓
YOLO
   ↓
Object Detection
   ↓
Target Center
   ↓
Robot
```

OBS는 그 과정을 실시간으로 보여준다.

---

# 67. LEVEL 5 — Depth Camera

RGB 영상뿐 아니라 실제 거리 정보를 사용한다.

```text
X
Y
Z
```

정보를 화면에 표시한다.

예:

```text
TARGET

X : 125 mm
Y : -37 mm
Z : 684 mm
```

---

# 68. LEVEL 6 — Robot Arm

최종적으로:

```text
Camera
↓
YOLO
↓
Depth Camera
↓
3D Position
↓
ROS 2
↓
MoveIt
↓
OpenManipulator
```

로 연결할 수 있다.

---

# 69. LEVEL 7 — AI Agent Studio

향후에는 사람이 직접 모든 프로그램을 실행하지 않아도 된다.

예:

```text
"로봇 카메라 시작해."
```

AI:

```text
Camera Start
YOLO Start
Robot Bringup
OBS Scene 변경
Recording Start
```

이런 자동 제작 시스템으로 발전할 수 있다.

---

# PART 27. GitHub를 책으로 발전시키기

README 한 파일에 모든 내용을 넣는 방법도 있지만 프로젝트가 커지면 챕터로 나누는 것이 좋다.

```text
README.md

docs/
├── chapter-01-introduction.md
├── chapter-02-obs.md
├── chapter-03-background-removal.md
├── chapter-04-ai-visualizer.md
├── chapter-05-robotics.md
├── chapter-06-github.md
└── chapter-07-troubleshooting.md
```

GitHub 자체가 온라인 기술 책이 된다.

---

# PART 28. 작업 로그를 남기는 습관

매일 작업이 끝날 때 다음 네 가지를 기록한다.

```text
오늘 무엇을 하려고 했는가?
무엇이 성공했는가?
무엇이 실패했는가?
다음에는 무엇을 할 것인가?
```

예:

```text
2026-08-21

목표:
OBS 웹캠 배경 제거

성공:
Background Removal 적용
웹캠 배경 제거
화면 크기 재조정
텍스트 확대
배경색 변경

문제:
화면이 복잡함
일부 영역 배치 불균형

해결:
불필요한 Source 축소
메인 화면 확대

다음 단계:
로봇 상태 정보를 OBS에 실시간 표시
```

이런 기록은 몇 달 뒤에 매우 중요한 자료가 된다.

---

# PART 29. AI 시대의 새로운 작업 방식

과거에는 새로운 프로그램을 배우려면 메뉴얼부터 읽었다.

이제는 방법이 달라질 수 있다.

```text
목표를 말한다
↓
AI와 대화한다
↓
일단 실행한다
↓
문제가 생긴다
↓
AI에게 로그를 보여준다
↓
수정한다
↓
다시 실행한다
```

이것은 단순히 코드를 생성하는 것이 아니다.

**AI와 함께 시스템을 만들어가는 방식**이다.

---

# PART 30. 이것이 바이브 코딩과 연결되는 이유

바이브 코딩의 핵심은 모든 코드를 완벽히 외우는 것이 아니다.

사람은 목적을 가지고 있다.

AI에게 목적을 설명한다.

AI와 반복적으로 수정하면서 결과에 접근한다.

예:

```text
"사람 뒤의 배경을 없애자."
```

↓

```text
Background Removal
```

다음:

```text
"글씨가 너무 작다."
```

↓

```text
Text Source 수정
```

다음:

```text
"화면이 복잡하다."
```

↓

```text
Crop / Resize / Layout
```

다음:

```text
"이 과정을 GitHub에 남기자."
```

↓

```text
Markdown + Git
```

이렇게 자연어가 시스템 설계 명령이 된다.

---

# PART 31. 앞으로 익혀야 할 핵심 스킬

앞으로 FOR MAKERS LAB에서 계속 발전시키면 좋은 기술은 다음과 같다.

```text
Linux Terminal
Git
GitHub
OBS Studio
Video Editing
Audio Mixing
Python
OpenCV
YOLO
Depth Camera
ROS 2
MoveIt
Dynamixel
AI Prompting
Automation
Technical Documentation
```

이 기술을 각각 따로 배우는 것이 아니라 하나의 프로젝트에서 연결하면 학습 속도가 훨씬 빨라진다.

---

# PART 32. 가장 중요한 제작 철학

완벽한 결과만 보여줄 필요는 없다.

오히려

```text
실패
↓
이유
↓
수정
↓
다시 실행
↓
성공
```

이 과정이 다른 사람에게 훨씬 가치 있는 자료가 될 수 있다.

---

# PART 33. FOR MAKERS LAB 제작 파이프라인

최종적으로 우리가 만들고 있는 구조는 다음과 같다.

```text
                 ┌──────────────┐
                 │     IDEA     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   ChatGPT    │
                 └──────┬───────┘
                        │
          ┌─────────────┼──────────────┐
          │             │              │
          ▼             ▼              ▼
       Python          ROS 2           OBS
          │             │              │
          ▼             ▼              ▼
        YOLO          Robot          Studio
          │             │              │
          └─────────────┼──────────────┘
                        │
                        ▼
                    RECORDING
                        │
                        ▼
                     EDITING
                        │
               ┌────────┴────────┐
               ▼                 ▼
            YouTube            GitHub
```

---

# PART 34. 오늘 얻은 가장 중요한 결과

오늘 완성한 것은 OBS 화면 하나가 아니다.

우리는 다음의 연결 방법을 연습했다.

```text
AI
+
Linux
+
OBS
+
Camera
+
Video
+
Git
+
GitHub
+
Robotics
```

그리고 이 모든 것을

**대화하면서 만들어냈다.**

이 점이 가장 중요하다.

---

# PART 35. 최종 Git 작업 명령

오늘 문서를 GitHub에 올릴 때 핵심 명령을 다시 정리한다.

프로젝트 폴더 이동:

```bash
cd ~/FOR-MAKERS-LAB/2026-08-21-ai-obs-studio
```

상태 확인:

```bash
git status
```

모든 변경 파일 추가:

```bash
git add .
```

Commit:

```bash
git commit -m "Add 2026-08-21 AI OBS Studio project book"
```

GitHub 업로드:

```bash
git push
```

확인:

```bash
git log --oneline -5
```

---

# PART 36. 한 번에 기억해야 할 Git 공식

Git을 처음 사용하는 사람이라면 이것만 먼저 기억해도 된다.

```bash
git status
```

↓

```bash
git add .
```

↓

```bash
git commit -m "오늘 작업 설명"
```

↓

```bash
git push
```

즉,

```text
확인
↓
선택
↓
기록
↓
업로드
```

이다.

---

# PART 37. 다음 프로젝트로 발전시키기

오늘의 문서를 끝이라고 생각하지 않는다.

GitHub에서 계속 업데이트한다.

예:

```text
v0.1
OBS 기본 화면

v0.2
Background Removal

v0.3
AI Visualizer

v0.4
YOLO

v0.5
Depth Camera

v0.6
Robot Control

v1.0
AI + Vision + Robot + OBS 통합
```

프로젝트가 발전하는 과정 자체를 기록한다.

---

# 마무리

오늘의 핵심은 Background Removal 플러그인을 설치했다는 것이 아니다.

OBS 기능을 하나 더 배웠다는 것도 아니다.

Git 명령어를 몇 개 배웠다는 것도 아니다.

가장 중요한 변화는 **작업 방식**이다.

사람이 아이디어를 말한다.

AI와 대화한다.

프로그램을 설치한다.

직접 실행한다.

문제가 발생한다.

문제를 다시 설명한다.

수정한다.

카메라가 작동한다.

AI가 사물을 인식한다.

로봇이 움직인다.

OBS가 그 과정을 기록한다.

YouTube가 사람들에게 보여준다.

GitHub가 기술을 남긴다.

그리고 다음 날 그 기록에서 다시 시작한다.

이것이 FOR MAKERS LAB이 만들어가는 작업 방식이다.

---

# 오늘 작업을 한 문장으로

**AI와 대화하면서 생각을 실제 시스템으로 만들고, 그 시스템이 만들어지는 과정까지 영상과 코드와 문서로 기록한다.**

---

# FOR MAKERS LAB

### Make → Test → Fail → Fix → Record → Share → Upgrade

**완성품만 기록하지 않는다.**

**만들어지는 과정을 기록한다.**

**그 과정이 다음 프로젝트의 기술이 된다.**
