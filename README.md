# 🤖 Multi-Agent Researcher

> LangGraph 기반 멀티에이전트 자동 리서치 시스템

주제 하나 입력하면 AI 에이전트 4개가 협력해서 리서치 보고서를 자동으로 생성해줍니다.

## 📸 Demo

![demo](https://github.com/user-attachments/assets/placeholder)

## 🏗️ 아키텍처

```
입력 (주제)
    ↓
🎯 Planner    → 최적 검색 쿼리 3개 자동 생성
    ↓
🔍 Researcher → DuckDuckGo 웹 검색 + 결과 수집
    ↓
🧠 Analyst    → 핵심 인사이트 추출 및 분석
    ↓
✍️ Writer     → 마크다운 리서치 보고서 완성
```

각 에이전트는 LangGraph StateGraph로 연결되어 있으며,  
실시간 SSE(Server-Sent Events)로 진행 상황이 UI에 스트리밍됩니다.

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| Agent Orchestration | LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Search | DuckDuckGo Search |
| Backend | FastAPI + SSE Streaming |
| Frontend | Vanilla JS (마크다운 렌더링) |

## 🚀 실행 방법

```bash
# 1. 레포 클론
git clone https://github.com/sauuri/multi-agent-researcher
cd multi-agent-researcher

# 2. 가상환경 설정
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 5. 서버 실행
uvicorn app.main:app --reload --port 8001
```

브라우저에서 `http://localhost:8001` 열기

## 📂 프로젝트 구조

```
multi-agent-researcher/
├── app/
│   ├── main.py        # FastAPI 엔드포인트 + SSE 스트리밍
│   ├── graph.py       # LangGraph 에이전트 정의 및 워크플로우
│   ├── tools.py       # 웹 검색 도구
│   ├── config.py      # 환경변수 설정
│   └── static/
│       └── index.html # 실시간 UI
├── requirements.txt
└── .env.example
```

## 💡 에이전트 역할

### 🎯 Planner
주제를 분석해 효과적인 검색 쿼리 3개를 생성합니다.

### 🔍 Researcher  
생성된 쿼리로 웹 검색을 실행하고 최신 정보를 수집합니다.

### 🧠 Analyst
수집된 데이터에서 핵심 인사이트와 패턴을 추출합니다.

### ✍️ Writer
분석 결과를 바탕으로 구조화된 마크다운 보고서를 작성합니다.

## 🔧 커스터마이징

`app/graph.py`에서 에이전트 프롬프트를 수정하거나  
노드를 추가해 워크플로우를 확장할 수 있습니다.

```python
# 새 에이전트 추가 예시
def fact_checker_node(state: ResearchState) -> dict:
    # 수집된 정보의 사실 여부 검증
    ...

workflow.add_node("fact_checker", fact_checker_node)
workflow.add_edge("researcher", "fact_checker")
workflow.add_edge("fact_checker", "analyst")
```
