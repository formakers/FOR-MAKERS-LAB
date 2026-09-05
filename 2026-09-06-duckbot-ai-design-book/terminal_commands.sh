#!/usr/bin/env bash
set -e

PROJECT='2026-09-06-duckbot-ai-design-book'
REPO="$HOME/FOR-MAKERS-LAB"
SRC="$HOME/Downloads/$PROJECT"

# 1) FOR-MAKERS-LAB 저장소로 이동
cd "$REPO"

# 2) 다운로드 폴더에서 프로젝트 복사
rm -rf "$PROJECT"
cp -a "$SRC" "$PROJECT"

# 3) 필요하면 오늘 다운로드한 추가 이미지를 직접 images 폴더에 복사
# 예:
# cp "$HOME/Downloads/추가이미지.png" "$PROJECT/images/"

# 4) Git 확인
git status

# 5) 추가 및 커밋
git add "$PROJECT"
git commit -m "Add DuckBot AI design book and video materials"

# 6) GitHub 업로드
git push origin main

# 7) 최종 확인
git status
