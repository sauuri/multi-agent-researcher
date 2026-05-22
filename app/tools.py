from tavily import TavilyClient
from app.config import settings


def web_search(query: str, max_results: int = 3) -> list[str]:
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query, max_results=max_results, search_depth="basic")
        results = response.get("results", [])
        return [
            f"[출처: {r.get('url', '')}]\n{r.get('content', '')}"
            for r in results
        ]
    except Exception as e:
        err = str(e)
        if "quota" in err.lower() or "limit" in err.lower() or "429" in err:
            raise RuntimeError("월간 검색 한도(1000회)를 초과했습니다. 다음 달에 다시 이용해주세요.")
        print(f"[search] {query}: {e}")
        return []
