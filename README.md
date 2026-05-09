# autonomous-mind

LLM에 내재적 동기를 주입하고, **호기심**과 **강박**이라는 두 에이전트가 자율적으로 지식을 탐색·검증하는 루프 시스템.

---

## 개념

LLM은 내재적 동기가 없다. 흉내만 낸다.

그렇다면 — 내재적 동기를 강제 주입하고, 예측 오차를 보상 신호로 삼는 두 에이전트를 붙이면 어떻게 될까?

```
[내재적 동기]  "나는 {domain} 최고 전문가가 되어야 한다"
      ↓
[뇌]  가설 생성: "X를 하면 한 발짝 나아간다"
      ↓               ↓
[호기심]           [강박]
예측 오차↑ = 보상↑   예측 오차↓ = 보상↑
(탐색)              (검증)
      ↓               ↓
   자기 채점         자기 채점  (0–10)
      ↓               ↓
[뇌]  종합 → Obsidian 노트 저장
      ↓
[비평가]  논리 오류 / 중복 / 근거 없는 주장 검토
      ↓
[뇌]  다음 가설 (비평 반영)
      ↓
  N시간 후 반복
```

---

## 에이전트 역할

| 에이전트 | 보상 조건 | 역할 |
|---------|----------|------|
| **뇌 (Brain)** | — | 가설 생성 → 스케줄링 → 종합. 교통 정리만 함 |
| **호기심 (Curiosity)** | 예측 오차가 클수록 보상↑ | 가설의 허점, 반례, 예상 밖 발견을 탐색 |
| **강박 (Compulsion)** | 예측 오차가 작을수록 보상↑ | 가설을 검증하고 수렴적 근거를 수집 |
| **비평가 (Critic)** | — | 세션 전체를 읽고 논리 오류·중복·일관성 문제를 지적 |

---

## 디렉터리 구조

```
autonomous-mind/
├── config/
│   ├── system.yaml        # 모델, 루프 간격, max_tokens
│   └── domain.md          # ★ 사용자 편집 — 전문 분야 목표
├── prompts/               # FIXED — 수정 금지
│   ├── brain.md
│   ├── curiosity.md
│   ├── compulsion.md
│   └── critic.md
├── src/
│   ├── orchestrator.py    # 사이클 진입점
│   ├── agents.py          # Hermes CLI subprocess 호출
│   ├── obsidian.py        # vault/ MD 파일 쓰기
│   └── state.py           # 상태 관리 (.state.json)
├── vault/
│   ├── MOC.md             # 전체 세션 인덱스
│   └── sessions/          # cycle-NNNN_YYYY-MM-DD_HH-MM.md
└── .claude/commands/
    ├── run-mind.md        # /run-mind  — 루프 시작
    ├── mind-status.md     # /mind-status — 현재 상태
    └── mind-stop.md       # /mind-stop  — 루프 중지
```

---

## 세션 노트 구조

매 사이클마다 `vault/sessions/` 에 Obsidian 노트 하나가 생성된다.

```markdown
# Cycle 0042 — 2026-05-09_14-00

## Hypothesis        ← 뇌가 생성한 가설
## Curiosity Agent   ← 탐색 결과 + 자기 채점
## Compulsion Agent  ← 검증 결과 + 자기 채점
## Brain Synthesis   ← 종합 + 다음 가설 씨앗
## Critic Review     ← 논리 오류 / 중복 / 수정 지시
```

---

## 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 도메인 설정

`config/domain.md` 를 열어 전문 분야 목표를 작성한다.

```markdown
## Expertise Goal
나는 로보틱스 제어 알고리즘 최고 전문가가 되어야 한다.

## Current Focus
PID 제어기의 파라미터 자동 튜닝 방법론

## Open Questions
- Ziegler-Nichols 방법이 비선형 시스템에서 왜 실패하는가?
```

### 3. Hermes CLI 확인

```bash
hermes --version
hermes doctor
```

이 버전은 Claude CLI를 직접 호출하지 않는다. 각 Brain/Curiosity/Compulsion/Critic 턴은 `hermes chat -q ... -Q` subprocess로 실행된다. `config/system.yaml`의 `model: ""` 값은 현재 Hermes 기본 provider/model을 사용한다는 뜻이다.

### 4. 루프 시작

한 사이클만 수동 실행:

```bash
cd /home/ubuntu/autonomous-mind
source .venv/bin/activate
python src/orchestrator.py
```

주기 실행은 Hermes cron으로 등록한다. 예:

```bash
hermes cron create 'every 6h'
```

Cron prompt에는 위 수동 실행 명령을 넣으면 된다.

---

## 커맨드

| 커맨드 | 동작 |
|--------|------|
| `/run-mind` | 루프 시작 + 첫 사이클 즉시 실행 |
| `/mind-status` | 현재 사이클, 마지막 가설, 누적 인사이트 확인 |
| `/mind-stop` | 루프 중지 |

수동으로 한 사이클만 실행하려면:

```bash
cd autonomous-mind
python src/orchestrator.py
```

---

## 설정 (`config/system.yaml`)

```yaml
model: claude-opus-4-7       # 사용할 Claude 모델
loop_interval_hours: 6       # 루프 간격 (시간)
max_tokens: 3000             # 에이전트당 최대 토큰
```

---

## 고정 vs 편집 가능

| 파일 | 수정 |
|------|------|
| `prompts/*.md` | **금지** — 시스템 동작의 불변 핵심 |
| `config/system.yaml` | 가능 — 모델·간격 조정 |
| `config/domain.md` | **권장** — 목표와 맥락을 계속 업데이트 |

---

## 이론적 배경

- **Active Inference** (Karl Friston) — 예측 오차 최소화/최대화를 보상으로 사용
- **Intrinsic Motivation in RL** — 외재적 보상 없이 호기심 기반 탐색
- **Explore-Exploit Tradeoff** — 호기심(탐색) ↔ 강박(활용)의 동시 운용
