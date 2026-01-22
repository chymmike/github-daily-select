# GitHub Trending Digest 實作計畫

每日自動抓取 GitHub Trending 前 5 名專案，使用 Gemini 2.5 Flash 生成中文摘要，並透過 Resend 發送 HTML 郵件通知。

## 功能規格

| 項目 | 規格 |
|------|------|
| 資料來源 | GitHub Trending（全語言，Daily） |
| 抓取數量 | 每日 Top 5 |
| LLM | Gemini 2.5 Flash（免費額度） |
| 摘要語言 | 繁體中文 |
| 摘要內容 | 項目介紹、解決的問題、技術棧、Stars、連結 |
| 儲存格式 | `data/YYYY-MM-DD.json` |
| 郵件服務 | Resend |
| 郵件格式 | HTML（摘要 + 連結） |
| 執行方式 | GitHub Action |
| 執行時間 | UTC 00:00（台灣時間 08:00） |

---

## 檔案結構

```
github-daily-select/
├── src/
│   ├── scraper.py      # 爬取 GitHub Trending
│   ├── readme.py       # 抓取 README via GitHub API
│   ├── summarizer.py   # Gemini 2.5 Flash 生成摘要
│   ├── mailer.py       # Resend 發送郵件
│   └── main.py         # 主流程
├── data/               # JSON 輸出
├── templates/
│   └── email.html      # 郵件 HTML 模板
├── docs/
│   └── implementation_plan.md
├── .github/workflows/
│   └── daily.yml       # GitHub Action
├── requirements.txt
├── .env.example
└── README.md
```

---

## 模組說明

### scraper.py

爬取 GitHub Trending 頁面，解析 Top 5 專案資訊：
- 使用 `httpx` + `selectolax`（比 BeautifulSoup 快）
- 提取：repo name, description, stars, language, repo URL
- 回傳 list of dict

### readme.py

透過 GitHub API 抓取 README：
- `GET /repos/{owner}/{repo}/readme`
- Header: `Accept: application/vnd.github.raw+json`
- 處理 404（有些 repo 沒有 README）
- 回傳原始 markdown 字串

### summarizer.py

使用 Gemini 2.5 Flash 生成摘要：
- 使用 `google-genai` SDK
- Prompt 設計：
  ```
  你是一個技術文章摘要專家。請根據以下 GitHub 專案的 README，用繁體中文生成摘要。

  請包含：
  1. 這個專案是什麼（一句話）
  2. 它解決什麼問題
  3. 使用的主要技術棧
  
  README:
  {readme_content}
  ```
- 回傳結構化摘要

### mailer.py

使用 Resend 發送郵件：
- 使用 `resend` Python SDK
- 載入 HTML 模板並填入資料
- 設定寄件者（需要驗證 domain 或用 Resend 預設）

### main.py

主流程整合：
```python
def main():
    # 1. 爬取 trending
    repos = scrape_trending(limit=5)
    
    # 2. 抓取各 repo 的 README
    for repo in repos:
        repo['readme'] = fetch_readme(repo['name'])
    
    # 3. 生成摘要
    for repo in repos:
        repo['summary'] = generate_summary(repo['readme'])
    
    # 4. 存成 JSON
    save_json(repos)
    
    # 5. 發送郵件
    send_email(repos)
```

---

## 資料結構

### JSON 輸出格式 (`data/YYYY-MM-DD.json`)

```json
{
  "date": "2026-01-22",
  "generated_at": "2026-01-22T08:00:00+08:00",
  "repos": [
    {
      "rank": 1,
      "name": "owner/repo-name",
      "url": "https://github.com/owner/repo-name",
      "description": "原始 description from GitHub",
      "stars": 12345,
      "today_stars": 500,
      "language": "Python",
      "readme": "... 原始 markdown ...",
      "summary": {
        "what": "這是一個...",
        "problem": "它解決了...",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
      }
    }
  ]
}
```

---

## GitHub Action

```yaml
name: Daily Trending Digest

on:
  schedule:
    - cron: '0 0 * * *'  # UTC 00:00 = UTC+8 08:00
  workflow_dispatch:  # 手動觸發

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run digest
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
        run: python src/main.py
      
      - name: Commit JSON data
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add data/
          git commit -m "chore: add daily digest $(date +%Y-%m-%d)" || exit 0
          git push
```

---

## Secrets 設定

在 GitHub repo → Settings → Secrets and variables → Actions 新增：

| Secret Name | 說明 |
|-------------|------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) 取得 |
| `RESEND_API_KEY` | [Resend Dashboard](https://resend.com/api-keys) 取得 |
| `EMAIL_TO` | 你的收件 email 地址 |

---

## 驗證計畫

### 本地測試

1. 設定 `.env` 檔案
2. 執行 `python src/main.py`
3. 確認 `data/` 目錄有生成 JSON
4. 確認收到郵件

### GitHub Action 測試

1. Push 到 GitHub
2. 手動觸發 workflow（workflow_dispatch）
3. 確認 Action 成功執行
4. 確認 JSON commit 到 repo
5. 確認收到郵件
