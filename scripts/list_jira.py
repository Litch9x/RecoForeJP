"""
RecoForeJP - Jira 現状リスト
全 Epic と、その下にぶら下がる Story を表示する。

使い方（環境変数が設定されている PowerShell で）:
    python scripts/list_jira.py
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_API_TOKEN", "")
SITE = os.environ.get("JIRA_SITE", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")


def die(msg, code=1):
    print(f"❌ {msg}")
    sys.exit(code)


def api(path):
    url = f"https://{SITE}{path}"
    auth = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        die(f"HTTP {e.code} on {path}: {e.read().decode()}")


def main():
    missing = [
        n
        for n, v in [
            ("JIRA_EMAIL", EMAIL),
            ("JIRA_API_TOKEN", TOKEN),
            ("JIRA_SITE", SITE),
            ("JIRA_PROJECT_KEY", PROJECT_KEY),
        ]
        if not v
    ]
    if missing:
        die(f"環境変数が未設定: {', '.join(missing)}")

    jql_epics = urllib.parse.urlencode(
        {
            "jql": f"project = {PROJECT_KEY} AND issuetype = Epic ORDER BY key ASC",
            "maxResults": 100,
            "fields": "summary,status",
        }
    )
    epics = api(f"/rest/api/3/search?{jql_epics}").get("issues", [])

    print(f"=== {PROJECT_KEY} の Epic と Story ===\n")
    for epic in epics:
        ek = epic["key"]
        es = epic["fields"]["summary"]
        est = epic["fields"]["status"]["name"]
        print(f"📦 {ek}  [{est}]  {es}")

        jql_children = urllib.parse.urlencode(
            {
                "jql": f"project = {PROJECT_KEY} AND parent = {ek} ORDER BY key ASC",
                "maxResults": 100,
                "fields": "summary,status",
            }
        )
        children = api(f"/rest/api/3/search?{jql_children}").get("issues", [])
        for c in children:
            ck = c["key"]
            cs = c["fields"]["summary"]
            cst = c["fields"]["status"]["name"]
            print(f"    └─ {ck}  [{cst}]  {cs}")
        print()


if __name__ == "__main__":
    main()
