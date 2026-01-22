"""
GitHub Trending 爬蟲
爬取 https://github.com/trending 頁面，解析 Top N 專案
"""

import httpx
from selectolax.parser import HTMLParser


def scrape_trending(limit: int = 5) -> list[dict]:
    """
    爬取 GitHub Trending 頁面
    
    Args:
        limit: 抓取前幾名，預設 5
    
    Returns:
        list of dict，每個 dict 包含：
        - rank: 排名
        - name: owner/repo
        - url: repo 完整 URL
        - description: 專案描述
        - language: 程式語言
        - stars: 總 star 數
        - today_stars: 今日新增 star 數
    """
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()
    
    parser = HTMLParser(response.text)
    repos = []
    
    # 每個 repo 是一個 article.Box-row
    articles = parser.css("article.Box-row")
    
    for i, article in enumerate(articles[:limit], start=1):
        # Repo name: h2 > a
        name_el = article.css_first("h2 a")
        if not name_el:
            continue
        
        # 取得 href，格式為 /owner/repo
        href = name_el.attributes.get("href", "").strip()
        name = href.lstrip("/")
        repo_url = f"https://github.com{href}"
        
        # Description: p.col-9
        desc_el = article.css_first("p.col-9")
        description = desc_el.text(strip=True) if desc_el else ""
        
        # Language: span[itemprop="programmingLanguage"]
        lang_el = article.css_first("span[itemprop='programmingLanguage']")
        language = lang_el.text(strip=True) if lang_el else None
        
        # Stars: 找包含 star 圖示的連結
        # 結構是 a href="/owner/repo/stargazers"
        stars = 0
        star_link = article.css_first(f"a[href='{href}/stargazers']")
        if star_link:
            stars_text = star_link.text(strip=True).replace(",", "")
            stars = _parse_stars(stars_text)
        
        # Today stars: 最後一個 span.d-inline-block
        today_stars = 0
        today_el = article.css_first("span.d-inline-block.float-sm-right")
        if today_el:
            today_text = today_el.text(strip=True).replace(",", "").split()[0]
            today_stars = _parse_stars(today_text)
        
        repos.append({
            "rank": i,
            "name": name,
            "url": repo_url,
            "description": description,
            "language": language,
            "stars": stars,
            "today_stars": today_stars,
        })
    
    return repos


def _parse_stars(text: str) -> int:
    """解析 star 數字，處理 1.2k 這種格式"""
    text = text.strip().lower()
    if not text:
        return 0
    
    try:
        if "k" in text:
            return int(float(text.replace("k", "")) * 1000)
        return int(text)
    except ValueError:
        return 0


if __name__ == "__main__":
    # 測試用
    results = scrape_trending(5)
    for repo in results:
        print(f"#{repo['rank']} {repo['name']} ⭐{repo['stars']} (+{repo['today_stars']})")
        print(f"   {repo['description'][:60]}...")
        print()
