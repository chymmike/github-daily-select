"""
Resend 郵件發送器
發送 HTML 格式的每日精選郵件
"""

import os
from datetime import datetime
from pathlib import Path

import resend


def send_digest_email(repos: list[dict], to_email: str | None = None) -> dict:
    """
    發送每日精選郵件
    
    Args:
        repos: repo 資訊列表，需有 summary 欄位
        to_email: 收件人 email，預設從環境變數取得
    
    Returns:
        Resend API 回應
    """
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY environment variable is required")
    
    resend.api_key = api_key
    
    to_email = to_email or os.environ.get("EMAIL_TO")
    if not to_email:
        raise ValueError("EMAIL_TO environment variable is required")
    
    # 載入並填充 HTML 模板
    html_content = _render_email(repos)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    response = resend.Emails.send({
        "from": "GitHub Daily Select <onboarding@resend.dev>",
        "to": [to_email],
        "subject": f"GitHub Trending - {today}",
        "html": html_content,
    })
    
    print(f"✓ Email sent to {to_email}")
    return response


def _render_email(repos: list[dict]) -> str:
    """渲染郵件 HTML"""
    template_path = Path(__file__).parent.parent / "templates" / "email.html"
    
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        # 使用內建模板 (Fallback)
        template = DEFAULT_TEMPLATE
    
    # 生成 repos HTML
    repos_html = ""
    for repo in repos:
        summary = repo.get("summary", {})
        tech_stack = summary.get("tech_stack", [])
        
        # 確保 tech_stack 是列表
        if isinstance(tech_stack, str):
            tech_stack = [tech_stack]
            
        tech_html = " ".join(f'<span class="tag">{t}</span>' for t in tech_stack)
        
        # 格式化數字
        stars_formatted = f"{repo.get('stars', 0):,}"
        
        repos_html += f"""
        <div class="repo-card">
            <div class="repo-header">
                <span class="rank">#{repo.get('rank', '?')}</span>
                <a href="{repo.get('url', '#')}" class="repo-name">{repo.get('name', 'Unknown')}</a>
                <span class="stars">★ {stars_formatted}</span>
            </div>
            
            <div class="description">
                {summary.get('what', 'No description available.')}
            </div>
            
            <div class="problem-statement">
                {summary.get('problem', '')}
            </div>
            
            <div class="tech-stack">
                {tech_html}
            </div>
        </div>
        """
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    return template.replace("{{DATE}}", today).replace("{{REPOS}}", repos_html)


DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GitHub Daily Select</title>
</head>
<body>
    <h1>GitHub Daily Select</h1>
    {{REPOS}}
</body>
</html>
"""


if __name__ == "__main__":
    # 測試用
    test_repos = [
        {
            "rank": 1,
            "name": "test/repo",
            "url": "https://github.com/test/repo",
            "stars": 12345,
            "summary": {
                "what": "這是一個測試專案",
                "problem": "用於測試郵件發送功能",
                "tech_stack": ["Python", "FastAPI"],
            },
        }
    ]
    
    html = _render_email(test_repos)
    Path("test_email.html").write_text(html)
    print("Test email saved to test_email.html")
