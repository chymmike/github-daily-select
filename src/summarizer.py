"""
Gemini 2.5 Flash 摘要生成器
根據 README 生成結構化的繁體中文摘要
"""

import json
import os
import time
from google import genai
from google.genai import types


def create_client() -> genai.Client:
    """建立 Gemini client"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    return genai.Client(api_key=api_key)


SUMMARY_PROMPT = """你是一個技術文章摘要專家。請根據以下 GitHub 專案的 README，用繁體中文生成摘要。

請以 JSON 格式回傳，包含以下欄位：
- what: 這個專案是什麼（一句話，30字以內）
- problem: 它解決什麼問題（2-3句話）
- tech_stack: 使用的主要技術棧（陣列，最多5個）

只回傳 JSON，不要有其他文字。

專案名稱: {repo_name}
專案描述: {description}
Stars: {stars}

README:
{readme}
"""


def generate_summary(
    repo_name: str,
    readme: str,
    description: str = "",
    stars: int = 0,
    client: genai.Client | None = None,
) -> dict:
    """
    使用 Gemini 2.5 Flash 生成專案摘要
    
    Args:
        repo_name: owner/repo 格式
        readme: README markdown 內容
        description: 專案描述
        stars: star 數量
        client: Gemini client（可選，會自動建立）
    
    Returns:
        dict 包含 what, problem, tech_stack
    """
    if not readme:
        return {
            "what": "無法取得 README",
            "problem": "此專案沒有 README 檔案",
            "tech_stack": [],
        }
    
    if client is None:
        client = create_client()
    
    # 截斷過長的 README（避免超過 token 限制）
    max_readme_length = 15000
    if len(readme) > max_readme_length:
        readme = readme[:max_readme_length] + "\n\n... (內容已截斷)"
    
    prompt = SUMMARY_PROMPT.format(
        repo_name=repo_name,
        description=description,
        stars=stars,
        readme=readme,
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )
        
        # 解析 JSON 回應
        text = response.text.strip()
        
        # 移除可能的 markdown code block
        if "```" in text:
            import re
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                # Fallback: simple strip
                text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)
    
    except json.JSONDecodeError as e:
        print(f"JSON parse error for {repo_name}: {e}")
        print(f"Raw text: {response.text}") # Debug output
        return {
            "what": "摘要生成失敗",
            "problem": f"JSON 解析錯誤: {str(e)}",
            "tech_stack": [],
        }
    except Exception as e:
        print(f"Error generating summary for {repo_name}: {e}")
        return {
            "what": "摘要生成失敗",
            "problem": str(e),
            "tech_stack": [],
        }


def generate_summaries(repos: list[dict]) -> list[dict]:
    """
    批次生成多個 repo 的摘要
    
    Args:
        repos: repo 資訊列表，需有 name, readme, description, stars
    
    Returns:
        更新後的 repos 列表，新增 'summary' 欄位
    """
    client = create_client()
    
    for repo in repos:
        print(f"Generating summary for {repo['name']}...")
        
        summary = generate_summary(
            repo_name=repo["name"],
            readme=repo.get("readme", ""),
            description=repo.get("description", ""),
            stars=repo.get("stars", 0),
            client=client,
        )
        
        repo["summary"] = summary
        print(f"  → {summary.get('what', 'N/A')}")
        
        # 避免觸發 Rate Limit (429 Resource Exhausted)
        # Free tier 限制較嚴格，加入 10 秒緩衝
        print("  ⏳ Waiting 10s to avoid rate limit...")
        time.sleep(10)
    
    return repos


if __name__ == "__main__":
    # 測試用（需設定 GEMINI_API_KEY）
    test_readme = """
    # FastAPI
    
    FastAPI framework, high performance, easy to learn, fast to code, ready for production.
    
    ## Features
    - Fast: Very high performance, on par with NodeJS and Go
    - Easy: Designed to be easy to use and learn
    - Automatic docs: Interactive API documentation
    """
    
    result = generate_summary(
        repo_name="tiangolo/fastapi",
        readme=test_readme,
        description="FastAPI framework",
        stars=75000,
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
