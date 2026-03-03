import requests
import os

def list_repos():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user/repos", headers=headers)
    if response.status_code == 200:
        return [{"name": r["name"], "url": r["html_url"]} for r in response.json()]
    return {"error": "Failed to fetch repos", "status": response.status_code}

def get_issue_count(owner, repo):
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response = requests.get(url, headers=headers)
    return len(response.json()) if response.status_code == 200 else 0