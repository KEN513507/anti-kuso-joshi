# Anti-Kuso-Joshi Project: Constitution (GEMINI.md)

## Objective
本プロジェクトの最終目的はコップ検出ではない。
目的は以下の通り：
- 人物状態観測
- 表情分析
- 長期ログ収集
- 状態推定

## Current Architecture
- **Edge**: XIAO ESP32S3 Sense (OV2640) -> MJPEG HTTP Stream
- **Host**: Ubuntu 24.04 (OpenCV + YOLOv8) -> Web Dashboard

## Current Status (Verified)
- [x] ESP32 Camera / Wi-Fi STA / MJPEG Streaming
- [x] OpenCV Capture / YOLOv8 Integration
- [x] Cup Detection Verification (PoC Completed)

## Roadmap
1. **Phase 1**: Camera Streaming (DONE)
2. **Phase 2**: Person Detection (ACTIVE)
3. **Phase 3**: Face Detection
4. **Phase 4**: Face Landmark
5. **Phase 5**: Expression Analysis
6. **Phase 6**: Behavior Modeling
7. **Phase 7**: Long-Term Audit Logging

## Engineering Rules
- Reproducibility first.
- Log everything.
- Verify before optimization.
- CPU fallback must always work.
- Never break working capture pipeline.
- Every feature requires objective evidence.

## Performance Policy
- **Current**: CPU inference.
- **Target**: GPU inference (GTX970 / CUDA 12.1 compatible).
- **Avoid**: CUDA 13 builds (Incompatible with current driver).

## AI Instructions
Before making any architectural proposal:
1. Preserve existing working pipeline.
2. Prefer objective verification over speculation.
3. Consider future expression-analysis requirements.
4. Cup detection is not the final goal.
5. Face analysis is higher priority than object classification.
6. Always provide terminal commands.
7. Always provide rollback steps.
8. Never propose cloud services unless explicitly requested.
9. Assume single developer project.
10. Optimize for Ubuntu 24.04.
