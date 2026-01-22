# GitHub Daily Select

每日自動抓取 GitHub Trending 前 5 名專案，使用 AI 生成中文摘要，並透過郵件發送精選通知。

## ✨ 功能

- 🔥 **自動抓取** — 每日爬取 GitHub Trending Top 5 專案
- 🤖 **AI 摘要** — 使用 Gemini 2.5 Flash 生成繁體中文摘要
- 📧 **郵件通知** — 透過 Resend 發送極簡風格 HTML 郵件
- 📦 **資料保存** — 每日結果存成 JSON 檔案
- ⏰ **自動執行** — GitHub Action 每日定時執行

## 🚀 快速開始

### 1. Clone 專案

```bash
git clone https://github.com/chymmike/github-daily-select.git
cd github-daily-select
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

複製 `.env.example` 為 `.env` 並填入你的 API keys：

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
EMAIL_TO=your_email@example.com
EMAIL_FROM=newsletter@yourdomain.com  # Optional: Default is onboarding@resend.dev
GITHUB_TOKEN=your_github_token  # Optional but recommended
```

### 4. 執行

```bash
python src/main.py
```

## ⚙️ GitHub Action 設定

### 設定 Secrets

在 GitHub repo → **Settings** → **Secrets and variables** → **Actions** 新增：

| Secret | 說明 |
|--------|------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) 取得 |
| `RESEND_API_KEY` | [Resend Dashboard](https://resend.com/api-keys) 取得 |
| `EMAIL_TO` | 收件 email 地址 |
| `EMAIL_FROM` | (選填) 自定義寄件人，需在 Resend 驗證 Domain |

### 執行時間

預設每日 **UTC 00:00**（台灣時間 08:00）自動執行。

也可以手動觸發：**Actions** → **Daily Trending Digest** → **Run workflow**

## 📁 專案結構

```
github-daily-select/
├── src/
│   ├── scraper.py      # 爬取 GitHub Trending
│   ├── readme.py       # 抓取 README
│   ├── summarizer.py   # Gemini 生成摘要
│   ├── mailer.py       # Resend 發送郵件
│   └── main.py         # 主流程
├── data/               # 每日 JSON 輸出
├── templates/
│   └── email.html      # 郵件模板
├── docs/
│   └── implementation_plan.md
└── .github/workflows/
    └── daily.yml
```

## 📊 輸出範例

每日產出 `data/YYYY-MM-DD.json`：

```json
{
  "date": "2026-01-22",
  "repos": [
    {
      "rank": 1,
      "name": "owner/repo",
      "stars": 12345,
      "summary": {
        "what": "這是一個...",
        "problem": "它解決了...",
        "tech_stack": ["Python", "FastAPI"]
      }
    }
  ]
}
```

## 📝 License

MIT
