#!/usr/bin/env python3
"""Local Skill Radar service: daily discovery, snapshots, and guarded installation."""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import http.client
import io
import json
import math
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
CURRENT_FILE = DATA_DIR / "current.json"
CONFIG_FILE = DATA_DIR / "config.json"
HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_DOWNLOAD = 30 * 1024 * 1024
MAX_SKILL_BYTES = 12 * 1024 * 1024
MAX_SKILL_FILES = 250
TOKEN = secrets.token_urlsafe(24)
REFRESH_LOCK = threading.Lock()

OFFICIAL_REPOS = [
    ("openai", "skills", "official"),
    ("anthropics", "skills", "official"),
    ("NVIDIA", "skills", "official"),
    ("vercel-labs", "agent-skills", "official"),
    ("NousResearch", "hermes-agent", "official"),
]

OPPORTUNITY = {
    "fit": .20, "demand": .10, "leverage": .15, "quality": .10,
    "github_heat": .15, "x_heat": .10, "momentum": .05,
    "maintenance": .10, "uniqueness": .05,
}
RISK = {
    "permissions": .25, "execution": .20, "network": .15, "secrets": .15,
    "obfuscation": .10, "provenance": .10, "mismatch": .05,
}

CATEGORY_RULES = [
    ("文档与办公", ("pdf", "document", "docx", "spreadsheet", "excel", "slides", "presentation")),
    ("研究与知识", ("research", "paper", "citation", "knowledge", "search", "wiki")),
    ("软件开发", ("code", "debug", "test", "github", "review", "deploy", "frontend", "backend")),
    ("销售与增长", ("sales", "lead", "buyer", "marketing", "seo", "content", "growth")),
    ("数据与分析", ("data", "sql", "analytics", "chart", "database", "etl")),
    ("安全与合规", ("security", "audit", "privacy", "compliance", "vulnerability")),
    ("媒体与创作", ("image", "video", "audio", "design", "creative", "media")),
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def weighted(scores: dict, weights: dict[str, float]) -> float:
    pairs = [(float(scores[k]), w) for k, w in weights.items() if scores.get(k) is not None]
    total = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / total if total else 0.0


def calculate_radar(scores: dict, hard_gate: bool = False) -> dict:
    opportunity = weighted(scores, OPPORTUNITY)
    risk = weighted(scores, RISK)
    confidence = clamp(scores.get("evidence_confidence", 0))
    value = clamp(opportunity * (.4 + .6 * confidence / 100) - .35 * risk)
    if hard_gate:
        action = "quarantine"
    elif value >= 75 and risk < 30 and confidence >= 70:
        action = "adopt"
    elif value >= 60:
        action = "test"
    elif value >= 40:
        action = "watch"
    else:
        action = "build"
    return {
        "opportunity": round(opportunity, 1),
        "confidence": round(confidence, 1),
        "risk": round(risk, 1),
        "value_score": round(value, 1),
        "action": action,
    }


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def atomic_write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def load_config() -> dict:
    default = {
        "daily_enabled": True,
        "daily_time": "08:00",
        "github_token_env": "GITHUB_TOKEN",
        "x_bearer_token_env": "X_BEARER_TOKEN",
        "x_enrich_limit": 20,
        "max_per_repo": 8,
        "extra_repos": [],
    }
    default.update(load_json(CONFIG_FILE, {}))
    return default


def request_bytes(
    url: str,
    *,
    accept: str = "application/json",
    max_bytes: int = MAX_DOWNLOAD,
    extra_headers: dict | None = None,
) -> bytes:
    headers = {"User-Agent": "SkillRadar/1.4", "Accept": accept}
    token_name = load_config().get("github_token_env", "GITHUB_TOKEN")
    if urllib.parse.urlparse(url).hostname == "api.github.com" and os.environ.get(token_name):
        headers["Authorization"] = f"Bearer {os.environ[token_name]}"
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, headers=headers)
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                length = int(response.headers.get("Content-Length") or 0)
                if length > max_bytes:
                    raise ValueError(f"响应过大：{length} bytes")
                data = response.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise ValueError("响应超过安全大小限制")
                return data
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(.7 * (attempt + 1))
    raise last_error


def request_json(url: str) -> dict:
    return json.loads(request_bytes(url).decode("utf-8"))


def github_api(path: str) -> dict:
    return request_json(f"https://api.github.com/{path.lstrip('/')}")


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        field = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if field:
            value = field.group(2).strip().strip("'\"")
            result[field.group(1)] = value
    return result


def choose_category(name: str, description: str, path: str) -> str:
    haystack = f"{name} {description} {path}".lower()
    for category, words in CATEGORY_RULES:
        if any(word in haystack for word in words):
            return category
    return "通用效率"


def infer_intent_cn(name: str, description: str, path: str, category: str) -> str:
    haystack = f"{name} {description} {path}".lower()
    rules = [
        (("spreadsheet", "excel", "sheets"), "创建、清洗、分析或验证电子表格"),
        (("pdf",), "读取、生成、转换或检查 PDF 文档"),
        (("slides", "presentation", "ppt"), "制作和优化演示文稿"),
        (("research", "paper", "citation", "wiki"), "开展资料研究、来源核验与知识整理"),
        (("github", "pull request", "code review", "review"), "处理代码仓库、评审或协作流程"),
        (("debug", "test", "qa", "quality"), "诊断问题、执行测试并形成可复现证据"),
        (("image", "design", "canvas", "art"), "生成、编辑或评估视觉内容"),
        (("video", "audio", "voice"), "处理视频、音频或多媒体生产流程"),
        (("deploy", "devops", "kubernetes", "docker"), "执行部署、运维与环境管理"),
        (("security", "audit", "privacy"), "进行安全检查、风险审计或隐私治理"),
        (("sales", "lead", "buyer", "outreach"), "开展客户开发、销售情报或触达准备"),
        (("seo", "content", "marketing"), "规划内容、SEO 或市场增长工作"),
        (("email", "gmail"), "处理邮件检索、整理与回复工作流"),
        (("calendar", "schedule", "meeting"), "安排日程、会议与时间协调"),
        (("skill", "agent"), "创建、维护或编排 Agent 的可复用能力"),
        (("browser", "website", "frontend", "web "), "构建、检查或操作网站与前端界面"),
    ]
    for words, intent in rules:
        if any(word in haystack for word in words):
            return intent
    return f"标准化{category}相关任务"


def explain_in_chinese(name: str, description: str, category: str, text: str, path: str) -> dict:
    lower = text.lower()
    capabilities = []
    if "##" in text:
        headings = re.findall(r"^#{2,3}\s+(.+)$", text, re.M)[:5]
        if headings:
            capabilities.append("按明确章节组织工作步骤")
    if "scripts/" in lower or "python" in lower or "bash" in lower:
        capabilities.append("可能配合脚本完成可重复操作")
    if "references/" in lower or "reference" in lower:
        capabilities.append("会按需读取参考资料")
    if "verification" in lower or "validate" in lower or "test" in lower:
        capabilities.append("包含验证或测试要求")
    if not capabilities:
        capabilities.append("通过 SKILL.md 为 Agent 提供可复用的任务流程")

    audience = {
        "文档与办公": "经常处理正式文档、表格或演示材料的人",
        "研究与知识": "需要检索、核验来源并形成结论的研究者和知识工作者",
        "软件开发": "开发者、技术团队与代码审查人员",
        "销售与增长": "销售、外贸、市场与内容增长团队",
        "数据与分析": "数据分析师、运营与业务决策人员",
        "安全与合规": "安全、审计、合规和平台工程团队",
        "媒体与创作": "设计、视频、音频和内容创作者",
    }.get(category, "希望把重复任务标准化的个人或团队")
    intent = infer_intent_cn(name, description, path, category)
    summary = (
        f"这是一个“{category}”类 Skill，主要用于{intent}。"
        f"它会把「{name}」相关任务整理成 Agent 可以稳定重复执行的步骤，减少临时发挥和遗漏。"
    )
    return {
        "summary_cn": summary,
        "best_for_cn": audience,
        "how_it_works_cn": "；".join(capabilities) + "。",
        "typical_use_cn": f"当任务涉及 {category}，并且需要一致输出、减少遗漏或沉淀团队方法时使用。",
        "path_note_cn": f"Skill 位于仓库路径 `{path}`；安装前应同时检查该目录中的脚本、依赖与资源文件。",
    }


def infer_platforms(text: str, repo: str, path: str) -> list[str]:
    haystack = f"{text}\n{repo}\n{path}".lower()
    platforms = ["通用 SKILL.md"]
    rules = {
        "Codex": ("codex", "openai/skills", ".codex"),
        "Claude": ("claude", "anthropic", ".claude"),
        "Hermes": ("hermes", "nousresearch"),
        "Cursor": ("cursor", ".cursor"),
        "GitHub Copilot": ("copilot", "github agent"),
    }
    for platform, terms in rules.items():
        if any(term in haystack for term in terms):
            platforms.append(platform)
    return platforms


def risk_scan(text: str) -> tuple[dict, bool, list[str]]:
    lower = text.lower()
    findings = []

    def present(pattern: str) -> bool:
        return re.search(pattern, lower, re.I | re.M) is not None

    permissions = 10
    execution = 8
    network = 8
    secrets_score = 4
    obfuscation = 0
    if present(r"\b(sudo|administrator|root privileges|chmod 777)\b"):
        permissions = 75
        findings.append("请求高权限或宽泛文件权限")
    if present(r"\b(rm\s+-rf|del\s+/[sq]|format\s+[a-z]:|shutdown)\b"):
        execution = 95
        findings.append("包含潜在破坏性命令")
    elif present(r"\b(eval|exec|subprocess|powershell|bash|cmd\.exe)\b"):
        execution = 48
        findings.append("包含命令或代码执行能力")
    if present(r"(curl|wget|invoke-webrequest).{0,80}(\||iex|bash|sh)"):
        execution = max(execution, 88)
        network = max(network, 75)
        findings.append("存在下载后直接执行模式")
    elif present(r"https?://|requests\.|urllib|fetch\("):
        network = 42
        findings.append("需要访问外部网络")
    if present(r"(api[_ -]?key|token|password|credential|\.ssh|\.env)"):
        secrets_score = 62
        findings.append("可能读取或使用凭据")
    if present(r"(base64.{0,40}(decode|b64decode)|fromcharcode|compressed payload)"):
        obfuscation = 82
        findings.append("存在编码或混淆执行信号")
    hard_gate = execution >= 90 or (obfuscation >= 70 and execution >= 45)
    return {
        "permissions": permissions, "execution": execution, "network": network,
        "secrets": secrets_score, "obfuscation": obfuscation,
    }, hard_gate, findings


def repo_momentum(repo: dict) -> int:
    pushed = repo.get("pushed_at")
    if not pushed:
        return 45
    try:
        days = max(0, (datetime.now().astimezone() - datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days)
    except ValueError:
        return 45
    return round(clamp(92 - math.log1p(days) * 13))


def repo_demand(stars: int) -> int:
    return round(clamp(25 + math.log10(max(1, stars) + 1) * 13))


def task_demand(category: str, description: str) -> int:
    base = {
        "文档与办公": 84, "研究与知识": 80, "软件开发": 82,
        "销售与增长": 78, "数据与分析": 80, "安全与合规": 76,
        "媒体与创作": 72, "通用效率": 70,
    }.get(category, 68)
    if len(description) >= 80:
        base += 4
    return round(clamp(base))


def x_recent_signal(candidate: dict, bearer_token: str) -> tuple[int | None, dict]:
    name = re.sub(r"[^A-Za-z0-9._-]+", " ", candidate["name"]).strip()
    repo = candidate["repo"]
    terms = [f'"{name}"'] if name else []
    terms.append(f'"{repo}"')
    query = f"({' OR '.join(terms)}) -is:retweet"
    params = urllib.parse.urlencode({
        "query": query,
        "max_results": 100,
        "tweet.fields": "created_at,public_metrics,author_id",
    })
    url = f"https://api.x.com/2/tweets/search/recent?{params}"
    try:
        payload = json.loads(request_bytes(
            url,
            extra_headers={"Authorization": f"Bearer {bearer_token}"},
        ).decode("utf-8"))
    except Exception as exc:
        return None, {"status": "error", "error": str(exc)[:180], "query": query}
    posts = payload.get("data") or []
    authors = {post.get("author_id") for post in posts if post.get("author_id")}
    engagement = 0
    likes = reposts = replies = quotes = 0
    for post in posts:
        metrics = post.get("public_metrics") or {}
        likes += int(metrics.get("like_count") or 0)
        reposts += int(metrics.get("retweet_count") or 0)
        replies += int(metrics.get("reply_count") or 0)
        quotes += int(metrics.get("quote_count") or 0)
    engagement = likes + reposts * 2 + replies + quotes * 2
    volume_score = clamp(math.log1p(len(posts)) * 20)
    engagement_score = clamp(math.log1p(engagement) * 12)
    diversity_score = clamp(len(authors) / max(1, len(posts)) * 100)
    heat = round(volume_score * .45 + engagement_score * .40 + diversity_score * .15)
    return heat, {
        "status": "ok", "window_days": 7, "posts": len(posts),
        "authors": len(authors), "likes": likes, "reposts": reposts,
        "replies": replies, "quotes": quotes, "engagement": engagement,
        "query": query,
    }


def enrich_x_signals(candidates: list[dict], config: dict) -> str:
    token = os.environ.get(config.get("x_bearer_token_env", "X_BEARER_TOKEN"), "")
    if not token:
        for candidate in candidates:
            candidate["scores"]["x_heat"] = None
            candidate["x_signal"] = {"status": "unavailable", "reason": "missing_bearer_token"}
            candidate["radar"] = calculate_radar(candidate["scores"], candidate.get("hard_gate", False))
        return "unavailable"
    limit = max(0, min(50, int(config.get("x_enrich_limit", 20))))
    targets = sorted(candidates, key=lambda x: x["radar"]["value_score"], reverse=True)[:limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        future_map = {pool.submit(x_recent_signal, item, token): item for item in targets}
        for future in concurrent.futures.as_completed(future_map):
            item = future_map[future]
            heat, signal = future.result()
            item["scores"]["x_heat"] = heat
            item["x_signal"] = signal
            if heat is not None:
                item["scores"]["evidence_confidence"] = clamp(item["scores"]["evidence_confidence"] + 5)
            item["radar"] = calculate_radar(item["scores"], item.get("hard_gate", False))
            item["action"] = item["radar"]["action"]
    target_ids = {item["id"] for item in targets}
    for item in candidates:
        if item["id"] not in target_ids:
            item["scores"]["x_heat"] = None
            item["x_signal"] = {"status": "not_sampled", "reason": "outside_enrichment_limit"}
            item["radar"] = calculate_radar(item["scores"], item.get("hard_gate", False))
    return "ok"


def discover_repo(
    owner: str,
    repo_name: str,
    source: str,
    max_skills: int,
    keyword: str | None = None,
) -> list[dict]:
    repo = github_api(f"repos/{owner}/{repo_name}")
    branch = repo.get("default_branch", "main")
    tree = github_api(f"repos/{owner}/{repo_name}/git/trees/{urllib.parse.quote(branch)}?recursive=1")
    excluded_parts = {"test", "tests", "fixture", "fixtures", "e2e", "example", "examples", "sample", "samples"}
    paths = []
    path_shas = {}
    for item in tree.get("tree", []):
        path_value = item.get("path", "")
        parts = {part.lower() for part in PurePosixPath(path_value).parts}
        if item.get("type") == "blob" and path_value.endswith("SKILL.md") and not parts.intersection(excluded_parts):
            paths.append(path_value)
            path_shas[path_value] = item.get("sha")
    keyword_lower = (keyword or "").casefold()
    preferred = sorted(paths, key=lambda p: (
        keyword_lower not in p.casefold() if keyword_lower else False,
        not (p.startswith("skills/") or p.startswith("optional-skills/")),
        p.count("/"), p.lower()
    ))[:max_skills]
    results = []
    stars = int(repo.get("stargazers_count") or 0)
    for skill_file in preferred:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{urllib.parse.quote(branch)}/{urllib.parse.quote(skill_file, safe='/')}"
        try:
            text = request_bytes(raw_url, accept="text/plain", max_bytes=500_000).decode("utf-8", errors="replace")
        except Exception:
            continue
        front = parse_frontmatter(text)
        skill_path = str(PurePosixPath(skill_file).parent)
        name = front.get("name") or PurePosixPath(skill_path).name
        description = front.get("description", "").strip()
        if keyword_lower:
            terms = [term for term in re.split(r"\s+", keyword_lower) if term]
            searchable = f"{name}\n{description}\n{skill_path}\n{text}".casefold()
            if not all(term in searchable for term in terms):
                continue
        category = choose_category(name, description, skill_path)
        risk_values, hard_gate, findings = risk_scan(text)
        headings = len(re.findall(r"^##\s+", text, re.M))
        quality = clamp(42 + min(28, headings * 4) + (12 if description else 0) + (8 if len(text) > 1200 else 0))
        demand = task_demand(category, description)
        github_heat = repo_demand(stars)
        momentum = repo_momentum(repo)
        maintenance = round(clamp((momentum + (85 if repo.get("archived") is False else 25)) / 2))
        leverage = 82 if any(word in text.lower() for word in ("automate", "workflow", "repeat", "generate", "analy")) else 68
        uniqueness = 62 + (8 if category in ("安全与合规", "研究与知识") else 0)
        scores = {
            "fit": 72, "demand": demand, "leverage": leverage, "quality": round(quality),
            "github_heat": github_heat, "x_heat": None, "momentum": momentum,
            "maintenance": maintenance, "uniqueness": uniqueness,
            **risk_values, "provenance": 4 if source == "official" else 26, "mismatch": 5,
            "evidence_confidence": 90 if source == "official" else 75,
        }
        radar = calculate_radar(scores, hard_gate)
        explanation = explain_in_chinese(name, description, category, text, skill_path)
        content_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        revision = path_shas.get(skill_file) or content_sha256
        results.append({
            "id": f"{owner}/{repo_name}/{skill_path}",
            "name": name,
            "author": owner,
            "repo": f"{owner}/{repo_name}",
            "branch": branch,
            "skill_path": skill_path,
            "source": source,
            "url": f"https://github.com/{owner}/{repo_name}/tree/{branch}/{skill_path}",
            "skill_md_url": f"https://github.com/{owner}/{repo_name}/blob/{branch}/{skill_file}",
            "purpose": explanation["summary_cn"],
            "description": description,
            "category": category,
            "platforms": infer_platforms(text, f"{owner}/{repo_name}", skill_path),
            "explanation_cn": explanation,
            "scores": scores,
            "radar": radar,
            "action": radar["action"],
            "hard_gate": hard_gate,
            "evidence": [
                f"仓库 Stars：{stars:,}",
                f"仓库最近更新：{repo.get('pushed_at', '未知')}",
                f"来源级别：{'官方/厂商' if source == 'official' else '社区发现'}",
            ],
            "caveats": findings or ["自动扫描未发现明显高危模式；安装前仍需人工查看脚本和依赖。"],
            "repo_stars": stars,
            "repo_updated_at": repo.get("pushed_at"),
            "license": (repo.get("license") or {}).get("spdx_id"),
            "skill_revision": revision,
            "content_sha256": content_sha256,
            "version_label": f"rev-{revision[:8]}",
            "observed_at": now_iso(),
        })
    return results


def search_github_skills(keyword: str, limit: int = 12) -> dict:
    keyword = re.sub(r"\s+", " ", keyword).strip()
    if not 2 <= len(keyword) <= 80:
        raise ValueError("关键词长度必须为 2–80 个字符")
    if any(ord(char) < 32 for char in keyword):
        raise ValueError("关键词包含无效控制字符")
    limit = max(1, min(20, int(limit)))
    current = load_json(CURRENT_FILE, {})
    terms = [term for term in keyword.casefold().split(" ") if term]
    results = []
    indexed_repos = set()
    for item in current.get("candidates", []):
        if not item.get("repo"):
            continue
        indexed_repos.add(str(item["repo"]).casefold())
        searchable = " ".join([
            str(item.get("name", "")), str(item.get("description", "")),
            str(item.get("purpose", "")), str(item.get("category", "")),
            str(item.get("skill_path", "")), str(item.get("repo", "")),
        ]).casefold()
        if all(term in searchable for term in terms):
            candidate = dict(item)
            candidate["search_query"] = keyword
            candidate["search_result"] = True
            candidate["search_origin"] = "verified-index"
            results.append(candidate)

    repos = []
    seen = set(indexed_repos)

    def add_repo(full_name: str, source: str = "github"):
        if "/" not in full_name:
            return
        owner, repo_name = full_name.split("/", 1)
        key = full_name.casefold()
        if key not in seen:
            seen.add(key)
            repos.append((owner, repo_name, source))

    safe_query = re.sub(r'["/:]+', " ", keyword)
    query = urllib.parse.quote(f"{safe_query} agent skills in:name,description,readme")
    errors = []
    try:
        found = github_api(f"search/repositories?q={query}&sort=stars&order=desc&per_page=3")
        for repo in found.get("items", []):
            add_repo(str(repo.get("full_name", "")), "github")
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            errors.append({"source": "github-search", "error": "GitHub API 限流，已返回本地核验索引结果"})
        else:
            raise

    repos = repos[:3]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        future_map = {
            pool.submit(discover_repo, owner, repo_name, source, 16, keyword): f"{owner}/{repo_name}"
            for owner, repo_name, source in repos
        }
        for future in concurrent.futures.as_completed(future_map):
            repo_name = future_map[future]
            try:
                results.extend(future.result())
            except Exception as exc:
                errors.append({"source": repo_name, "error": str(exc)[:180]})
    deduped = {item["id"].casefold(): item for item in results}
    results = list(deduped.values())
    for item in results:
        item["search_query"] = keyword
        item["search_result"] = True
        item.setdefault("search_origin", "github-live")
    results.sort(key=lambda item: (
        keyword.casefold() not in item["name"].casefold(),
        -item["radar"]["value_score"],
        -int(item.get("repo_stars") or 0),
    ))
    return {
        "query": keyword,
        "searched_repos": len(indexed_repos) + len(repos),
        "live_repos": len(repos),
        "count": min(len(results), limit),
        "candidates": results[:limit],
        "errors": errors,
    }


def trending_repos(limit: int = 3) -> list[tuple[str, str, str]]:
    query = urllib.parse.quote("topic:agent-skills stars:>20")
    try:
        data = github_api(f"search/repositories?q={query}&sort=updated&order=desc&per_page={limit}")
    except Exception:
        return []
    output = []
    official = {f"{a}/{b}".lower() for a, b, _ in OFFICIAL_REPOS}
    for item in data.get("items", []):
        full = item.get("full_name", "")
        if "/" in full and full.lower() not in official:
            owner, repo = full.split("/", 1)
            output.append((owner, repo, "github"))
    return output


def compare_previous(candidates: list[dict], previous: dict) -> None:
    old = {item.get("id"): item for item in previous.get("candidates", [])}
    observed_at = now_iso()
    for item in candidates:
        prior = old.get(item["id"])
        item["is_new"] = prior is None
        prior_hash = prior.get("content_sha256") if prior else None
        changed = bool(prior_hash and item.get("content_sha256") != prior_hash)
        item["updated_since_last"] = changed
        item["update_status"] = (
            "new" if prior is None else "baseline" if not prior_hash else "updated" if changed else "unchanged"
        )
        item["previous_revision"] = prior.get("skill_revision") if prior else None
        item["last_skill_update_at"] = (
            observed_at if changed or prior is None else prior.get("last_skill_update_at")
        )
        changes = []
        if changed:
            changes.append("SKILL.md 内容指纹发生变化")
            old_risk = float(prior.get("radar", {}).get("risk", 0))
            new_risk = float(item.get("radar", {}).get("risk", 0))
            if abs(new_risk - old_risk) >= 5:
                changes.append(f"风险分 {old_risk:.0f} → {new_risk:.0f}")
            old_quality = float(prior.get("scores", {}).get("quality", 0))
            new_quality = float(item.get("scores", {}).get("quality", 0))
            if abs(new_quality - old_quality) >= 5:
                changes.append(f"质量分 {old_quality:.0f} → {new_quality:.0f}")
        item["change_summary"] = changes
        if prior:
            star_delta = max(0, int(item.get("repo_stars") or 0) - int(prior.get("repo_stars") or 0))
            velocity = clamp(30 + math.log1p(star_delta) * 18) if star_delta else 25
            base_heat = float(item["scores"].get("github_heat") or 0)
            item["scores"]["github_heat"] = round(base_heat * .75 + velocity * .25)
            item["github_signal"] = {
                "stars": int(item.get("repo_stars") or 0),
                "star_delta": star_delta,
                "heat": item["scores"]["github_heat"],
            }
            item["radar"] = calculate_radar(item["scores"], item.get("hard_gate", False))
            item["action"] = item["radar"]["action"]
            delta = item["radar"]["value_score"] - float(prior.get("radar", {}).get("value_score", 0))
            item["delta"] = round(delta, 1)
            item["status"] = "rising" if delta >= 3 else "cooling" if delta <= -3 else "stable"
        else:
            item["github_signal"] = {
                "stars": int(item.get("repo_stars") or 0),
                "star_delta": None,
                "heat": item["scores"].get("github_heat"),
            }
            item["delta"] = 0
            item["status"] = "new"
        prior_history = list(prior.get("history", [])) if prior else []
        if prior and not prior_history:
            prior_history.append({
                "observed_at": prior.get("observed_at") or previous.get("meta", {}).get("observed_at"),
                "value": prior.get("radar", {}).get("value_score"),
                "risk": prior.get("radar", {}).get("risk"),
                "stars": prior.get("repo_stars"),
                "github_heat": prior.get("scores", {}).get("github_heat"),
                "x_heat": prior.get("scores", {}).get("x_heat"),
                "revision": prior.get("skill_revision"),
            })
        point = {
            "observed_at": observed_at,
            "value": item["radar"]["value_score"],
            "risk": item["radar"]["risk"],
            "stars": item.get("repo_stars"),
            "github_heat": item.get("scores", {}).get("github_heat"),
            "x_heat": item.get("scores", {}).get("x_heat"),
            "revision": item.get("skill_revision"),
        }
        if prior_history and str(prior_history[-1].get("observed_at", ""))[:10] == observed_at[:10]:
            prior_history[-1] = point
        else:
            prior_history.append(point)
        item["history"] = prior_history[-30:]


def infer_gaps(candidates: list[dict]) -> list[dict]:
    groups = {}
    for item in candidates:
        groups.setdefault(item["category"], []).append(item)
    gaps = []
    for category, items in groups.items():
        avg_demand = sum(i["scores"]["demand"] for i in items) / len(items)
        avg_quality = sum(i["scores"]["quality"] for i in items) / len(items)
        avg_risk = sum(i["radar"]["risk"] for i in items) / len(items)
        opportunity = clamp(avg_demand - avg_quality * .25 + avg_risk * .35)
        if opportunity >= 45:
            gaps.append({
                "title": f"更可靠的{category} Skill",
                "reason": f"该类需求信号较强，但当前候选平均质量 {avg_quality:.0f}、风险 {avg_risk:.0f}，仍有改进空间。",
                "score": round(opportunity),
            })
    return sorted(gaps, key=lambda x: x["score"], reverse=True)[:3]


def refresh_snapshot() -> dict:
    with REFRESH_LOCK:
        config = load_config()
        previous = load_json(CURRENT_FILE, {})
        repos = list(OFFICIAL_REPOS)
        for value in config.get("extra_repos", []):
            if isinstance(value, str) and "/" in value:
                owner, repo = value.split("/", 1)
                repos.append((owner, repo, "github"))
        repos.extend(trending_repos())
        seen_repos = set()
        candidates = []
        errors = []
        unique_repos = []
        for owner, repo, source in repos:
            key = f"{owner}/{repo}".lower()
            if key not in seen_repos:
                seen_repos.add(key)
                unique_repos.append((owner, repo, source))
        max_per_repo = int(config.get("max_per_repo", 8))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            future_map = {
                pool.submit(discover_repo, owner, repo, source, max_per_repo): (owner, repo)
                for owner, repo, source in unique_repos
            }
            for future in concurrent.futures.as_completed(future_map):
                owner, repo = future_map[future]
                try:
                    candidates.extend(future.result())
                except Exception as exc:
                    errors.append({"source": f"{owner}/{repo}", "error": str(exc)[:240]})
        deduped = {item["id"].lower(): item for item in candidates}
        candidates = list(deduped.values())
        x_status = enrich_x_signals(candidates, config)
        compare_previous(candidates, previous)
        candidates.sort(key=lambda x: x["radar"]["value_score"], reverse=True)
        snapshot = {
            "meta": {
                "observed_at": now_iso(),
                "window_days": 30,
                "baseline": not bool(previous.get("candidates")),
                "demo": False,
                "online": True,
                "sources_scanned": len(seen_repos),
                "x_status": x_status,
                "x_enriched": sum(1 for item in candidates if item.get("scores", {}).get("x_heat") is not None),
                "updated_skills": sum(1 for item in candidates if item.get("updated_since_last")),
                "removed_skills": len({
                    item.get("id") for item in previous.get("candidates", [])
                } - {item.get("id") for item in candidates}),
                "errors": errors,
            },
            "candidates": candidates,
            "gaps": infer_gaps(candidates),
        }
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        date_name = datetime.now().strftime("snapshot-%Y-%m-%d.json")
        atomic_write(DATA_DIR / date_name, snapshot)
        atomic_write(CURRENT_FILE, snapshot)
        return snapshot


def safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip(".-_").lower()
    if not value or value in {".", ".."}:
        raise ValueError("无效 Skill 名称")
    return value[:64]


def find_candidate(candidate_id: str) -> dict:
    snapshot = load_json(CURRENT_FILE, {})
    for item in snapshot.get("candidates", []):
        if item.get("id") == candidate_id:
            return item
    raise ValueError("当前快照中找不到该 Skill")


def download_skill(candidate: dict, destination: Path) -> None:
    repo = candidate["repo"]
    branch = candidate.get("branch", "main")
    path = PurePosixPath(candidate["skill_path"])
    git = shutil.which("git")
    if git:
        with tempfile.TemporaryDirectory(prefix="skill-radar-git-") as temp_dir:
            clone_dir = Path(temp_dir) / "repo"
            env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
            clone = subprocess.run(
                [git, "-c", "protocol.file.allow=never", "clone", "--depth", "1", "--filter=blob:none",
                 "--sparse", "--branch", branch, f"https://github.com/{repo}.git", str(clone_dir)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, env=env,
            )
            if clone.returncode == 0:
                sparse = subprocess.run(
                    [git, "-C", str(clone_dir), "sparse-checkout", "set", "--no-cone", str(path)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, env=env,
                )
                if sparse.returncode == 0:
                    source = clone_dir / Path(*path.parts)
                    if not (source / "SKILL.md").is_file():
                        raise ValueError("目标目录中没有 SKILL.md")
                    files = [item for item in source.rglob("*") if item.is_file()]
                    if any(item.is_symlink() for item in source.rglob("*")):
                        raise ValueError("Skill 包含符号链接，已拒绝自动安装")
                    total = sum(item.stat().st_size for item in files)
                    if len(files) > MAX_SKILL_FILES or total > MAX_SKILL_BYTES:
                        raise ValueError("Skill 文件数量或体积超过安全限制")
                    if any(item.stat().st_size > 5 * 1024 * 1024 for item in files):
                        raise ValueError("Skill 内单个文件超过 5MB")
                    shutil.copytree(source, destination)
                    return
    archive_url = f"https://codeload.github.com/{repo}/zip/refs/heads/{urllib.parse.quote(branch)}"
    try:
        archive_bytes = request_bytes(archive_url, accept="application/zip", max_bytes=MAX_DOWNLOAD)
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            prefix_parts = None
            selected = []
            total = 0
            for info in archive.infolist():
                parts = PurePosixPath(info.filename).parts
                if len(parts) < 2:
                    continue
                if prefix_parts is None:
                    prefix_parts = parts[0]
                relative_repo = PurePosixPath(*parts[1:])
                try:
                    relative = relative_repo.relative_to(path)
                except ValueError:
                    continue
                if info.is_dir():
                    continue
                if any(part in {"", ".."} for part in relative.parts):
                    raise ValueError("源码压缩包包含不安全路径")
                if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                    raise ValueError("Skill 包含符号链接，已拒绝自动处理")
                if info.file_size > 5 * 1024 * 1024:
                    raise ValueError("Skill 内单个文件超过 5MB")
                total += info.file_size
                selected.append((info, relative))
            if not selected or not any(rel.as_posix() == "SKILL.md" for _, rel in selected):
                raise ValueError("源码压缩包中没有目标 SKILL.md")
            if len(selected) > MAX_SKILL_FILES or total > MAX_SKILL_BYTES:
                raise ValueError("Skill 文件数量或体积超过安全限制")
            destination.mkdir(parents=True, exist_ok=False)
            base = destination.resolve()
            for info, relative in selected:
                target = (destination / Path(*relative.parts)).resolve()
                if base not in target.parents:
                    raise ValueError("目标路径越界")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info))
            return
    except (OSError, urllib.error.URLError, zipfile.BadZipFile):
        if destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
    tree = github_api(f"repos/{repo}/git/trees/{urllib.parse.quote(branch)}?recursive=1")
    matching = []
    total = 0
    for item in tree.get("tree", []):
        if item.get("type") != "blob":
            continue
        item_path = PurePosixPath(item.get("path", ""))
        try:
            relative = item_path.relative_to(path)
        except ValueError:
            continue
        if any(part in {"..", ""} for part in relative.parts):
            raise ValueError("仓库包含不安全路径")
        size = int(item.get("size") or 0)
        if size > 5 * 1024 * 1024:
            raise ValueError("Skill 内单个文件超过 5MB")
        total += size
        matching.append((item_path, relative, size, item.get("url")))
    if not matching or not any(str(rel).replace("\\", "/") == "SKILL.md" for _, rel, _, _ in matching):
        raise ValueError("目标目录中没有 SKILL.md")
    if len(matching) > MAX_SKILL_FILES or total > MAX_SKILL_BYTES:
        raise ValueError("Skill 文件数量或体积超过安全限制")
    destination.mkdir(parents=True, exist_ok=False)
    base = destination.resolve()
    def fetch_file(entry):
        item_path, relative, size, blob_url = entry
        target = (destination / Path(*relative.parts)).resolve()
        if base not in target.parents:
            raise ValueError("目标路径越界")
        blob = request_json(blob_url)
        if blob.get("encoding") != "base64":
            raise ValueError(f"无法安全解码文件：{item_path}")
        content = base64.b64decode(blob.get("content", ""), validate=False)
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("Skill 内单个文件超过 5MB")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch_file, matching))


def install_codex(candidate: dict) -> dict:
    if candidate.get("hard_gate") or candidate.get("action") == "quarantine":
        raise PermissionError("该候选触发安全隔离，禁止一键安装")
    name = safe_name(candidate["name"])
    root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"
    destination = root / name
    if destination.exists():
        raise FileExistsError(f"目标已存在：{destination}")
    root.mkdir(parents=True, exist_ok=True)
    temporary = root / f".{name}.installing-{secrets.token_hex(4)}"
    try:
        download_skill(candidate, temporary)
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {"target": "codex", "path": str(destination), "restart_required": True}


def install_hermes(candidate: dict) -> dict:
    if candidate.get("hard_gate") or candidate.get("action") == "quarantine":
        raise PermissionError("该候选触发安全隔离，禁止一键安装")
    hermes = None if os.environ.get("SKILL_RADAR_SKIP_HERMES_CLI") == "1" else shutil.which("hermes")
    identifier = candidate["id"]
    if hermes:
        process = subprocess.run(
            [hermes, "skills", "install", identifier],
            capture_output=True, text=True, timeout=180,
        )
        if process.returncode != 0:
            raise RuntimeError((process.stderr or process.stdout or "Hermes 安装失败")[-800:])
        return {"target": "hermes", "path": "~/.hermes/skills/", "via": "hermes-cli", "message": process.stdout[-500:]}
    name = safe_name(candidate["name"])
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    destination = hermes_home / "skills" / "radar" / name
    if destination.exists():
        raise FileExistsError(f"目标已存在：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / f".{name}.installing-{secrets.token_hex(4)}"
    try:
        download_skill(candidate, temporary)
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {"target": "hermes", "path": str(destination), "via": "safe-copy"}


def export_portable(candidate: dict) -> dict:
    if candidate.get("hard_gate") or candidate.get("action") == "quarantine":
        raise PermissionError("该候选触发安全隔离，禁止导出可安装包")
    name = safe_name(candidate["name"])
    with tempfile.TemporaryDirectory(prefix="skill-radar-export-") as temp_dir:
        skill_dir = Path(temp_dir) / name
        download_skill(candidate, skill_dir)
        manifest = {
            "schema": "skill-radar-portable/v1",
            "name": candidate.get("name"),
            "source": candidate.get("url"),
            "canonical_id": candidate.get("id"),
            "revision": candidate.get("skill_revision"),
            "platforms": candidate.get("platforms") or ["通用 SKILL.md"],
            "exported_at": now_iso(),
        }
        instructions = f"""# {candidate.get('name')} 通用 Skill 包

此压缩包保留原始 Skill 目录结构和 `SKILL.md`。

## 安装

- Codex：把 `{name}` 文件夹复制到 `$CODEX_HOME/skills/` 或 `~/.codex/skills/`。
- Claude 兼容 Agent：把完整文件夹导入该 Agent 的 Skills 目录。
- Hermes：优先使用 `hermes skills install {candidate.get('id')}`；也可手动导入完整文件夹。
- 其他支持 `SKILL.md` 的 Agent：导入完整文件夹，不要只复制单个 Markdown 文件。

安装前请检查脚本、依赖、联网行为和凭据需求。来源：{candidate.get('url')}
"""
        archive_path = Path(temp_dir) / f"{name}-portable.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    archive.write(file_path, f"{name}/{file_path.relative_to(skill_dir).as_posix()}")
            archive.writestr(f"{name}/skill-radar-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr(f"{name}/INSTALL.zh-CN.md", instructions)
        encoded = base64.b64encode(archive_path.read_bytes()).decode("ascii")
    return {"filename": f"{name}-portable.zip", "content_base64": encoded, "manifest": manifest}


def schedule_command(enabled: bool, run_time: str) -> dict:
    if os.name != "nt":
        raise NotImplementedError("当前版本只支持在 Windows 中一键创建每日任务")
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", run_time):
        raise ValueError("时间格式必须是 HH:MM")
    task_name = "SkillRadarDailyUpdate"
    if not enabled:
        process = subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], capture_output=True, text=True)
        if process.returncode not in (0, 1):
            raise RuntimeError(process.stderr or process.stdout)
        config = load_config()
        config["daily_task_installed"] = False
        atomic_write(CONFIG_FILE, config)
        return {"enabled": False}
    command = str(APP_DIR / "每日更新.cmd")
    process = subprocess.run(
        ["schtasks", "/Create", "/SC", "DAILY", "/ST", run_time, "/TN", task_name, "/TR", command, "/F"],
        capture_output=True, text=True,
    )
    if process.returncode != 0:
        raise RuntimeError((process.stderr or process.stdout or "无法创建每日任务")[-800:])
    config = load_config()
    config.update({"daily_enabled": True, "daily_time": run_time, "daily_task_installed": True})
    atomic_write(CONFIG_FILE, config)
    return {"enabled": True, "time": run_time, "task": task_name}


def last_refresh() -> datetime | None:
    data = load_json(CURRENT_FILE, {})
    value = data.get("meta", {}).get("observed_at")
    try:
        return datetime.fromisoformat(value) if value else None
    except ValueError:
        return None


class RadarHandler(SimpleHTTPRequestHandler):
    server_version = "SkillRadar/1.4"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def log_message(self, format, *args):
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def end_headers(self):
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        super().end_headers()

    def json_response(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_000_000:
            raise ValueError("请求体大小无效")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def authorized(self) -> bool:
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://{HOST}:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
            return False
        return secrets.compare_digest(self.headers.get("X-Radar-Token", ""), TOKEN)

    def do_OPTIONS(self):
        self.send_error(HTTPStatus.FORBIDDEN)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/session":
            return self.json_response({"token": TOKEN, "service": "skill-radar", "version": "1.4"})
        if parsed.path == "/api/status":
            config = load_config()
            last = last_refresh()
            return self.json_response({
                "online": True,
                "refreshing": REFRESH_LOCK.locked(),
                "last_refresh": last.isoformat() if last else None,
                "next_refresh": (last + timedelta(days=1)).isoformat() if last else now_iso(),
                "daily_enabled": config.get("daily_enabled", True),
                "daily_time": config.get("daily_time", "08:00"),
                "daily_task_installed": config.get("daily_task_installed", False),
                "codex_path": str(Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"),
                "hermes_path": str(Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "skills"),
                "hermes_cli": bool(shutil.which("hermes")),
            })
        if parsed.path == "/api/snapshot":
            data = load_json(CURRENT_FILE, None)
            if data is None:
                return self.json_response({"error": "尚无联网快照"}, HTTPStatus.NOT_FOUND)
            return self.json_response(data)
        return super().do_GET()

    def do_POST(self):
        if not self.authorized():
            return self.json_response({"error": "请求未授权"}, HTTPStatus.FORBIDDEN)
        try:
            data = self.read_json()
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/refresh":
                snapshot = refresh_snapshot()
                return self.json_response({"ok": True, "snapshot": snapshot})
            if parsed.path == "/api/install":
                if data.get("confirm") is not True:
                    raise ValueError("必须明确确认安装")
                candidate = find_candidate(str(data.get("id", "")))
                target = data.get("target")
                result = install_codex(candidate) if target == "codex" else install_hermes(candidate) if target == "hermes" else None
                if result is None:
                    raise ValueError("安装目标必须是 codex 或 hermes")
                return self.json_response({"ok": True, **result})
            if parsed.path == "/api/export":
                candidate = find_candidate(str(data.get("id", "")))
                return self.json_response({"ok": True, **export_portable(candidate)})
            if parsed.path == "/api/search-github":
                result = search_github_skills(str(data.get("query", "")), int(data.get("limit", 12)))
                return self.json_response({"ok": True, **result})
            if parsed.path == "/api/schedule":
                result = schedule_command(bool(data.get("enabled")), str(data.get("time", "08:00")))
                return self.json_response({"ok": True, **result})
            return self.json_response({"error": "未知接口"}, HTTPStatus.NOT_FOUND)
        except PermissionError as exc:
            return self.json_response({"error": str(exc)}, HTTPStatus.FORBIDDEN)
        except FileExistsError as exc:
            return self.json_response({"error": str(exc)}, HTTPStatus.CONFLICT)
        except (ValueError, json.JSONDecodeError, NotImplementedError) as exc:
            return self.json_response({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except urllib.error.HTTPError as exc:
            message = f"联网请求失败：HTTP {exc.code}"
            if exc.code == 403:
                message += "；可能触发 GitHub 限流，可设置 GITHUB_TOKEN"
            return self.json_response({"error": message}, HTTPStatus.BAD_GATEWAY)
        except Exception as exc:
            return self.json_response({"error": f"操作失败：{str(exc)[:500]}"}, HTTPStatus.INTERNAL_SERVER_ERROR)


def scheduler_loop():
    while True:
        config = load_config()
        if config.get("daily_enabled", True):
            last = last_refresh()
            if last is None or datetime.now().astimezone() - last >= timedelta(hours=24):
                try:
                    refresh_snapshot()
                except Exception as exc:
                    print(f"每日更新失败：{exc}", file=sys.stderr)
        time.sleep(300)


def self_test() -> int:
    sample = """---
name: sample-research
description: Research and verify sources with a repeatable workflow.
---
# Sample
## Procedure
Use references and validate every claim.
"""
    front = parse_frontmatter(sample)
    assert front["name"] == "sample-research"
    risks, hard_gate, _ = risk_scan(sample)
    assert not hard_gate and risks["execution"] < 90
    scores = {
        "fit": 80, "demand": 75, "leverage": 80, "quality": 80, "momentum": 70,
        "github_heat": 72, "x_heat": None, "maintenance": 80, "uniqueness": 60,
        **risks, "provenance": 5, "mismatch": 0,
        "evidence_confidence": 85,
    }
    assert calculate_radar(scores)["value_score"] > 50
    assert "Codex" in infer_platforms("Use with Codex", "owner/repo", "skills/sample")
    current = [{
        "id": "owner/repo/sample", "content_sha256": "b" * 64, "skill_revision": "new",
        "repo_stars": 12, "scores": scores.copy(), "radar": calculate_radar(scores),
        "hard_gate": False,
    }]
    previous = {
        "meta": {"observed_at": "2026-06-30T08:00:00+08:00"},
        "candidates": [{
            "id": "owner/repo/sample", "content_sha256": "a" * 64, "skill_revision": "old",
            "repo_stars": 10, "scores": {**scores, "quality": 70},
            "radar": calculate_radar({**scores, "quality": 70}),
            "observed_at": "2026-06-30T08:00:00+08:00",
        }],
    }
    compare_previous(current, previous)
    assert current[0]["update_status"] == "updated"
    assert current[0]["updated_since_last"] is True
    assert len(current[0]["history"]) == 2
    print("Skill Radar server self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--refresh-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.refresh_only:
        snapshot = refresh_snapshot()
        print(f"Updated {len(snapshot['candidates'])} candidates.")
        return 0
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=scheduler_loop, daemon=True).start()
    server = ThreadingHTTPServer((HOST, args.port), RadarHandler)
    url = f"http://{HOST}:{args.port}/"
    print(f"Skill Radar 正在运行：{url}")
    print("关闭此窗口即可停止本地服务。")
    if not args.no_browser:
        threading.Timer(.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
