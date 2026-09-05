# Pretrained model placement

이 ZIP에는 대용량 학습 weight를 포함하지 않습니다.

기존 학습 모델 디렉터리 예:

```text
~/Downloads/pretrained_model/pretrained_model/
├── config.json
├── model.safetensors
├── policy_preprocessor.json
├── policy_preprocessor_step_3_normalizer_processor.safetensors
├── policy_postprocessor.json
├── policy_postprocessor_step_0_unnormalizer_processor.safetensors
└── train_config.json
```

실행 스크립트는 기본적으로 현재 작업 디렉터리(`MODEL_PATH="."`)에서 위 파일을 찾습니다.

GitHub에 weight를 배포해야 한다면 일반 Git commit 전에 파일 크기 제한을 확인하고 Git LFS 또는 모델 저장소 사용을 검토하세요.
