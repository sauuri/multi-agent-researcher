from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def web_search(query: str, max_results: int = 3) -> list[str]:
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results, time="y")
        tool = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")
        results = tool.invoke(query)
        if isinstance(results, list):
            return [
                f"[출처: {r.get('link', '')}]\n{r.get('snippet', r.get('body', str(r)))}"
                for r in results if isinstance(r, dict)
            ]
        return []
    except Exception as e:
        print(f"[search] {query}: {e}")
        return []
