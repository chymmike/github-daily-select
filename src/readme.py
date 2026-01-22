"""
GitHub README 抓取器
透過 GitHub API 取得 repo 的 README 內容
"""

import httpx


def fetch_readme(repo_name: str, token: str | None = None) -> str | None:
    """
    透過 GitHub API 抓取 README 原始內容
    
    Args:
        repo_name: owner/repo 格式
        token: GitHub token（可選，增加 rate limit）
    
    Returns:
        README markdown 內容，若無則回傳 None
    """
    url = f"https://api.github.com/repos/{repo_name}/readme"
    
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "github-daily-select",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = httpx.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            # Repo 沒有 README
            return None
        
        response.raise_for_status()
        return response.text
    
    except httpx.HTTPStatusError as e:
        print(f"Error fetching README for {repo_name}: {e}")
        return None
    except httpx.RequestError as e:
        print(f"Request error for {repo_name}: {e}")
        return None


def fetch_readmes(repos: list[dict], token: str | None = None) -> list[dict]:
    """
    批次抓取多個 repo 的 README
    
    Args:
        repos: repo 資訊列表，每個需有 'name' 欄位
        token: GitHub token
    
    Returns:
        更新後的 repos 列表，新增 'readme' 欄位
    """
    for repo in repos:
        readme = fetch_readme(repo["name"], token)
        repo["readme"] = readme
        
        if readme:
            print(f"✓ Fetched README for {repo['name']} ({len(readme)} chars)")
        else:
            print(f"✗ No README for {repo['name']}")
    
    return repos


if __name__ == "__main__":
    # 測試用
    test_repos = [
        {"name": "facebook/react"},
        {"name": "torvalds/linux"},
    ]
    
    results = fetch_readmes(test_repos)
    for repo in results:
        readme = repo.get("readme")
        if readme:
            print(f"{repo['name']}: {len(readme)} chars")
            print(readme[:200])
            print("---")
