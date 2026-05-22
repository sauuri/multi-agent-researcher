import json
import operator
import re
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.config import settings
from app.tools import web_search

llm = ChatOpenAI(
    model=settings.model_name,
    api_key=settings.openai_api_key,
    temperature=0.3,
)


# ── State ──────────────────────────────────────────────────────────────────────

class ResearchState(TypedDict):
    topic: str
    queries: list[str]
    results: list[str]
    analysis: str
    report: str
    logs: Annotated[list[str], operator.add]


# ── Nodes ──────────────────────────────────────────────────────────────────────

def planner_node(state: ResearchState) -> dict:
    """검색 쿼리 3개 생성"""
    response = llm.invoke([
        SystemMessage(content=(
            "You are a research planner. Given a topic, generate exactly 3 specific search queries "
            "in Korean to thoroughly research it. Return ONLY a JSON array of 3 strings, nothing else. "
            "Example: [\"쿼리1\", \"쿼리2\", \"쿼리3\"]"
        )),
        HumanMessage(content=f"주제: {state['topic']}"),
    ])

    try:
        match = re.search(r'\[.*?\]', response.content, re.DOTALL)
        queries = json.loads(match.group()) if match else [state["topic"]]
    except Exception:
        queries = [state["topic"]]

    return {
        "queries": queries[:3],
        "logs": [f"🎯 **플래너** — 검색 쿼리 {len(queries[:3])}개 생성: {', '.join(queries[:3])}"],
    }


def researcher_node(state: ResearchState) -> dict:
    """각 쿼리로 웹 검색"""
    all_results = []
    for q in state["queries"]:
        results = web_search(q, max_results=settings.max_search_results)
        all_results.extend(results)

    return {
        "results": all_results,
        "logs": [f"🔍 **리서처** — {len(all_results)}개 검색 결과 수집 완료"],
    }


def analyst_node(state: ResearchState) -> dict:
    """수집된 정보에서 핵심 인사이트 추출"""
    results_text = "\n\n---\n\n".join(state["results"][:9])

    response = llm.invoke([
        SystemMessage(content=(
            "You are a research analyst. Analyze the provided search results and extract "
            "key facts, insights, and patterns related to the topic. "
            "Be thorough and objective. Write your analysis in Korean."
        )),
        HumanMessage(content=(
            f"주제: {state['topic']}\n\n"
            f"검색 결과:\n{results_text}\n\n"
            "위 내용을 바탕으로 핵심 인사이트와 주요 내용을 분석해줘."
        )),
    ])

    return {
        "analysis": response.content,
        "logs": ["🧠 **분석가** — 핵심 인사이트 추출 완료"],
    }


def writer_node(state: ResearchState) -> dict:
    """분석 결과를 마크다운 보고서로 작성"""
    response = llm.invoke([
        SystemMessage(content=(
            "You are a professional report writer. Write a comprehensive research report in Korean "
            "using markdown format.\n\n"
            "Use this structure:\n"
            "# [주제] 리서치 보고서\n"
            "## 📌 요약\n"
            "## 🔍 주요 내용\n"
            "### (섹션별 소제목)\n"
            "## 💡 인사이트\n"
            "## ✅ 결론\n\n"
            "Be informative, clear, and well-structured."
        )),
        HumanMessage(content=(
            f"주제: {state['topic']}\n\n"
            f"분석 내용:\n{state['analysis']}\n\n"
            "위 내용을 바탕으로 최종 보고서를 작성해줘."
        )),
    ])

    return {
        "report": response.content,
        "logs": ["✍️ **작성가** — 최종 보고서 작성 완료"],
    }


# ── Graph ──────────────────────────────────────────────────────────────────────

workflow = StateGraph(ResearchState)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("writer", writer_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "writer")
workflow.add_edge("writer", END)

graph = workflow.compile()
