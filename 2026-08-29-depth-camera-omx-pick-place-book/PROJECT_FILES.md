# PROJECT FILES

```text
2026-08-29-depth-camera-omx-pick-place-book/
├── README.md
├── BOOK.md
├── PROJECT_FILES.md
└── images/
```

## 파일 설명

- `README.md` : GitHub 첫 화면용 프로젝트 소개
- `BOOK.md` : 전체 교육용 책 본문
- `PROJECT_FILES.md` : 프로젝트 파일 구조 설명
- `images/` : 유튜브 영상과 책에서 사용하는 시스템 도면 저장

## GitHub 업로드 예시

이미 `~/FOR-MAKERS-LAB` 저장소를 사용하고 있다면 다음과 같이 업로드할 수 있습니다.

```bash
cd ~/FOR-MAKERS-LAB

cp -r ~/Downloads/2026-08-29-depth-camera-omx-pick-place-book .

git status

git add 2026-08-29-depth-camera-omx-pick-place-book

git commit -m "Add Depth Camera OMX Pick and Place book"

git push origin main
```

다운로드 위치가 다르면 `cp` 명령의 원본 경로만 실제 위치에 맞게 변경하면 됩니다.
