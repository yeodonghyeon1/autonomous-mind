# Domain Configuration (USER EDITABLE)

## Expertise Goal
나는 ETRI Human Understanding AI Paper Challenge 2026 / DACON 생체·라이프로그 데이터 모델링 최고 전문가가 되어야 한다.

## Current Focus
`/home/ubuntu/dacon-new` 레포의 ETRI 2026 DACON 솔루션을 계속 개선한다. 현재 안전한 기준선은 `main.py` v9 16-seed × 5-fold + Beta calibration이며, README 기준 OOF 0.5740 / LB 0.5995(ref)이다. `iter118.py`는 OOF 0.5592로 최고지만 LB 0.6135로 실패했으므로 과적합/OOF-LB mismatch를 비판적으로 다뤄야 한다.

## Known Knowledge
- 데이터 경로는 `/home/ubuntu/dacon-new/data/` 이다.
- 주요 실행 파일: `main.py`, `iter112.py`, `iter118.py`.
- 제출 안전 우선순위는 README 기준 `main.py`가 가장 높다.
- `iter112.py`는 LGBM+CatBoost+XGB+LabelSeq+ContrastiveAlign 9-member ensemble이며 LB plateau 문제가 있다.
- `iter118.py`는 per-target stacking blend로 OOF는 좋지만 LB가 악화된 BIAS-22 paradigm over-optimism 사례다.
- 제출 파일은 UTF-8, 헤더 포함, random_state 고정이 필요하다.

## Open Questions
- 왜 iter118의 OOF 개선이 LB로 전이되지 않았는가?
- target별 calibration/Beta correction이 실제 LB 분포와 어떻게 어긋나는가?
- 추가 feature engineering이 leaderboard overfit 없이 generalization을 개선할 수 있는가?
- validation scheme을 어떻게 바꾸면 OOF-LB mismatch를 줄일 수 있는가?

## Constraints
- `prompts/*.md`는 시스템 동작의 불변 핵심이므로 수정하지 않는다.
- 실험은 `/home/ubuntu/dacon-new`에서 수행하고, autonomous-mind는 가설/검증/비평/Obsidian 기록 루프로 사용한다.
- Hermes subprocess가 Claude CLI 대신 Brain/Curiosity/Compulsion/Critic 역할을 수행한다.
