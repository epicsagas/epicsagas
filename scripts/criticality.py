#!/usr/bin/env python3
"""Score all original public repos in the epicsagas GitHub account with OpenSSF criticality_score.

Writes:
  criticality/ranking.json  - full per-repo records, score descending
  criticality/README.md     - human-readable Top 5 + full ranking

Run locally:  export GITHUB_TOKEN=$(gh auth token) && python scripts/criticality.py
In CI:        GITHUB_TOKEN is the default workflow token.
"""
import json
import os
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from json import JSONDecoder

ORG = os.environ.get("CRITICALITY_ORG", "epicsagas")
# criticality_score is expected on PATH (installed via pip in CI / venv locally).
CRIT_BIN = os.environ.get("CRITICALITY_BIN", "criticality_score")


def gh_get(url, token):
    req = urllib.request.Request(
        url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def list_repos(token):
    repos = []
    page = 1
    while True:
        batch = gh_get(
            f"https://api.github.com/users/{ORG}/repos?per_page=100&page={page}&type=public",
            token,
        )
        if not batch:
            break
        for repo in batch:
            if not repo["fork"] and not repo["archived"]:
                repos.append(repo["html_url"])
        if len(batch) < 100:
            break
        page += 1
    return repos


def score(url, token):
    env = dict(os.environ, GITHUB_TOKEN=token, GITHUB_AUTH_TOKEN=token)
    try:
        out = subprocess.run(
            [CRIT_BIN, "--repo", url, "--format", "json"],
            capture_output=True, text=True, timeout=180, env=env,
        )
        txt = (out.stdout or "") + (out.stderr or "")
        start = txt.find("{")
        if start < 0:
            return {"name": url.split("/")[-1], "url": url, "error": "no json output"}
        return JSONDecoder().raw_decode(txt[start:])[0]
    except Exception as e:
        return {"name": url.split("/")[-1], "url": url, "error": str(e)[:120]}


def fmt(d, key, default="-"):
    v = d.get(key, default)
    return v if v is not None else default


def write_readme(path, records, generated_at, total):
    top5 = records[:5]
    meta_names = {"epicsagas"}  # org profile metadata repo, not a real project

    lines = [
        "# OpenSSF Criticality Score",
        "",
        f"> OpenSSF criticality scores for `{ORG}` public repos (forks and archived excluded). "
        "Updated weekly by GitHub Actions.",
        "",
        f"**Updated:** {generated_at} · **Repos:** {total}",
        "",
        "## Top 5",
        "",
        "| # | score | repo | stars | contributors | commits/wk | releases |",
        "|---|-------|------|-------|--------------|-----------|----------|",
    ]
    for i, r in enumerate(top5, 1):
        tag = " _(meta)_" if r["name"] in meta_names else ""
        lines.append(
            f"| {i} | **{fmt(r, 'criticality_score'):.5f}** "
            f"| [{r['name']}]({r.get('url', '')}){tag} "
            f"| {fmt(r, 'watchers_count')} | {fmt(r, 'contributor_count')} "
            f"| {fmt(r, 'commit_frequency')} | {fmt(r, 'recent_releases_count')} |"
        )

    lines += [
        "",
        "<details><summary>Full ranking</summary>",
        "",
        "| # | score | repo | stars | contributors | commits/wk | age(mo) | releases |",
        "|---|-------|------|-------|--------------|-----------|---------|----------|",
    ]
    for i, r in enumerate(records, 1):
        lines.append(
            f"| {i} | {fmt(r, 'criticality_score'):.5f} "
            f"| [{r['name']}]({r.get('url', '')}) "
            f"| {fmt(r, 'watchers_count')} | {fmt(r, 'contributor_count')} "
            f"| {fmt(r, 'commit_frequency')} | {fmt(r, 'created_since')} "
            f"| {fmt(r, 'recent_releases_count')} |"
        )
    lines += ["", "</details>", ""]

    lines += [
        "## Notes",
        "",
        "- Scores range 0–1 and weigh contributor count, commit frequency, releases, issue activity, and dependents in addition to stars.",
        "- `dependents_count` currently reads as 0 — the main factor keeping scores low.",
        "- `_(meta)_` marks the account profile metadata repo, not a real project.",
        "- Tool: [`ossf/criticality_score`](https://github.com/ossf/criticality_score) Python version (officially deprecated; Go version recommended).",
        "- Machine-readable data: [`ranking.json`](./ranking.json)",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN (or GH_TOKEN) is required")

    os.makedirs("criticality", exist_ok=True)
    repos = list_repos(token)
    print(f"scoring {len(repos)} original repos...")

    records = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(score, u, token): u for u in repos}
        for f in as_completed(futs):
            records.append(f.result())

    ok = [r for r in records if "criticality_score" in r]
    fail = [r for r in records if "error" in r]
    ok.sort(key=lambda x: x.get("criticality_score", 0), reverse=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "generated_at": generated_at,
        "org": ORG,
        "count": len(ok),
        "failed": fail,
        "repos": ok,
    }
    with open("criticality/ranking.json", "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    write_readme("criticality/README.md", ok, generated_at, len(ok))

    print(f"OK: {len(ok)}/{len(repos)}  FAILED: {len(fail)}")
    for r in fail:
        print("  FAIL:", r["name"], "-", r.get("error", ""))
    print("top1:", ok[0]["name"], ok[0]["criticality_score"] if ok else "-")
    print("wrote criticality/ranking.json, criticality/README.md")


if __name__ == "__main__":
    main()
