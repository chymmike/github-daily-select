"""
GitHub Daily Select - 主流程
每日抓取 GitHub Trending，生成摘要，發送郵件
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from scraper import scrape_trending
from readme import fetch_readmes
from summarizer import generate_summaries
from mailer import send_digest_email


def main():
    """主流程"""
    # 載入 .env（本地開發用）
    load_dotenv()
    
    print("=" * 50)
    print("GitHub Daily Select")
    print("=" * 50)
    
    # 1. 爬取 Trending
    print("\n📊 Step 1: Scraping GitHub Trending...")
    repos = scrape_trending(limit=5)
    print(f"   Found {len(repos)} repos")
    
    for repo in repos:
        print(f"   #{repo['rank']} {repo['name']} ⭐{repo['stars']}")
    
    # 2. 抓取 README
    print("\n📖 Step 2: Fetching READMEs...")
    github_token = os.environ.get("GITHUB_TOKEN")
    repos = fetch_readmes(repos, token=github_token)
    
    # 3. 生成摘要
    print("\n🤖 Step 3: Generating summaries with Gemini...")
    repos = generate_summaries(repos)
    
    # 4. 儲存 JSON
    print("\n💾 Step 4: Saving JSON...")
    save_json(repos)
    
    # 5. 發送郵件
    print("\n📧 Step 5: Sending email...")
    try:
        send_digest_email(repos)
    except Exception as e:
        print(f"   ⚠️ Failed to send email: {e}")
    
    print("\n✅ Done!")


def save_json(repos: list[dict]) -> Path:
    """儲存結果到 JSON 檔案"""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = data_dir / f"{today}.json"
    
    output = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "repos": repos,
    }
    
    filepath.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    
    print(f"   Saved to {filepath}")
    return filepath


if __name__ == "__main__":
    main()
