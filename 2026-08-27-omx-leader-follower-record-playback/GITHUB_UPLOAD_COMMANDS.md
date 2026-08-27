# GitHub 업로드 명령

압축을 푼 뒤 프로젝트 폴더를 기존 FOR-MAKERS-LAB 저장소 안으로 복사했다고 가정합니다.

```bash
cd ~/FOR-MAKERS-LAB

git status

git add 2026-08-27-omx-leader-follower-record-playback/

git commit -m "Add OMX Leader Follower record and smooth playback project"

git push origin main
```

## 다운로드 폴더에서 바로 복사하는 예

```bash
cd ~/FOR-MAKERS-LAB

cp -r ~/Downloads/2026-08-27-omx-leader-follower-record-playback \
~/FOR-MAKERS-LAB/

git add 2026-08-27-omx-leader-follower-record-playback/

git commit -m "Add OMX Leader Follower record and smooth playback project"

git push origin main
```
