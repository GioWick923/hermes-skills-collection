const OPPORTUNITY_WEIGHTS = {
  fit: .20, demand: .10, leverage: .15, quality: .10,
  github_heat: .15, x_heat: .10, momentum: .05,
  maintenance: .10, uniqueness: .05
};
const RISK_WEIGHTS = {
  permissions: .25, execution: .20, network: .15, secrets: .15,
  obfuscation: .10, provenance: .10, mismatch: .05
};
const LABELS = {
  fit: "任务匹配", demand: "真实需求", leverage: "效率杠杆", quality: "交付质量",
  github_heat: "GitHub 热度", x_heat: "X 热度", momentum: "增长动能",
  maintenance: "维护健康", uniqueness: "差异优势"
};

const demoData = {
  meta: { observed_at: "2026-07-01T09:30:00+08:00", window_days: 30, baseline: false, demo: true },
  candidates: [
    {
      id: "openai/skills/spreadsheets", name: "Spreadsheets", author: "OpenAI", source: "official",
      url: "https://github.com/openai/skills", purpose: "创建、清洗和分析高质量电子表格",
      description: "把公式、格式、图表和验证流程封装成可重复使用的表格工作流。",
      scores: { fit: 92, demand: 88, leverage: 91, quality: 94, momentum: 78, maintenance: 91, uniqueness: 72, permissions: 12, execution: 14, network: 6, secrets: 2, obfuscation: 0, provenance: 3, mismatch: 0, evidence_confidence: 94 },
      delta: 6.8, status: "rising", is_new: false, action: "adopt",
      evidence: ["官方来源与清晰许可", "工作流完整，包含验证步骤", "适用于高频办公任务"],
      caveats: ["复杂工作簿仍需人工复核公式和视觉布局"]
    },
    {
      id: "openai/skills/pdfs", name: "PDF Toolkit", author: "OpenAI", source: "official",
      url: "https://github.com/openai/skills", purpose: "读取、生成、渲染并验证 PDF",
      description: "覆盖提取、生成、页面渲染和视觉检查，适合正式文档交付。",
      scores: { fit: 86, demand: 82, leverage: 88, quality: 93, momentum: 70, maintenance: 90, uniqueness: 68, permissions: 10, execution: 16, network: 2, secrets: 0, obfuscation: 0, provenance: 3, mismatch: 0, evidence_confidence: 93 },
      delta: 2.1, status: "stable", is_new: false, action: "adopt",
      evidence: ["官方目录", "包含渲染与视觉验证", "通用文档场景覆盖广"],
      caveats: ["扫描件 OCR 质量取决于原始文件"]
    },
    {
      id: "community/research/evidence-first", name: "Evidence First", author: "Field Notes Lab", source: "github",
      url: "https://github.com/", purpose: "把多源研究整理成可核验的结论",
      description: "强调来源分级、冲突证据和结论置信度的研究工作流。",
      scores: { fit: 84, demand: 87, leverage: 82, quality: 80, momentum: 89, maintenance: 76, uniqueness: 83, permissions: 18, execution: 8, network: 42, secrets: 4, obfuscation: 0, provenance: 24, mismatch: 5, evidence_confidence: 75 },
      delta: 18.4, status: "rising", is_new: true, action: "test",
      evidence: ["多个独立社区出现相同需求", "近期提交活跃", "输出结构可复用"],
      caveats: ["非官方来源", "需要联网检索，必须核验引用"]
    },
    {
      id: "community/sales/buyer-intel", name: "Buyer Intel", author: "Outbound Stack", source: "directory",
      url: "https://skills.sh/", purpose: "目标客户画像与买家情报整理",
      description: "从公开来源形成结构化客户情报卡，并记录证据与置信度。",
      scores: { fit: 78, demand: 90, leverage: 85, quality: 72, momentum: 84, maintenance: 67, uniqueness: 76, permissions: 30, execution: 12, network: 55, secrets: 14, obfuscation: 0, provenance: 32, mismatch: 8, evidence_confidence: 68 },
      delta: 12.7, status: "rising", is_new: true, action: "test",
      evidence: ["外贸与销售场景需求强", "目录增长信号明显", "字段结构较完整"],
      caveats: ["必须遵守隐私和反垃圾邮件规则", "公开联系方式也需合法使用"]
    },
    {
      id: "nvidia/skills/cuda-optimization", name: "CUDA Optimizer", author: "NVIDIA", source: "official",
      url: "https://github.com/NVIDIA/skills", purpose: "定位 GPU 性能瓶颈并给出优化路径",
      description: "针对 CUDA 工程的诊断和性能调优流程，专业度高但适用面较窄。",
      scores: { fit: 42, demand: 64, leverage: 90, quality: 92, momentum: 73, maintenance: 94, uniqueness: 91, permissions: 15, execution: 35, network: 4, secrets: 0, obfuscation: 0, provenance: 2, mismatch: 0, evidence_confidence: 91 },
      delta: 3.5, status: "stable", is_new: false, action: "watch",
      evidence: ["厂商官方维护", "专业壁垒高", "目标用户明确"],
      caveats: ["对非 GPU 用户价值有限", "运行诊断可能需要本机编译环境"]
    },
    {
      id: "community/content/short-video-factory", name: "Video Factory", author: "Creator Loop", source: "community",
      url: "https://skillsmd.dev/", purpose: "短视频选题、脚本和素材流水线",
      description: "把内容生产拆成可批量运行的步骤，但目前同质化较高。",
      scores: { fit: 68, demand: 83, leverage: 79, quality: 61, momentum: 77, maintenance: 58, uniqueness: 35, permissions: 14, execution: 22, network: 35, secrets: 10, obfuscation: 0, provenance: 39, mismatch: 12, evidence_confidence: 62 },
      delta: -2.7, status: "cooling", is_new: false, action: "build",
      evidence: ["需求长期存在", "同类方案数量很多", "缺少稳定评测"],
      caveats: ["输出容易模板化", "平台规则变化快"]
    },
    {
      id: "community/dev/session-handoff", name: "Session Handoff", author: "Continuity Tools", source: "github",
      url: "https://github.com/", purpose: "跨会话保存工程上下文与验证状态",
      description: "生成经过验证的交接文件，让复杂任务在新会话中继续推进。",
      scores: { fit: 80, demand: 79, leverage: 86, quality: 84, momentum: 68, maintenance: 73, uniqueness: 70, permissions: 18, execution: 12, network: 0, secrets: 22, obfuscation: 0, provenance: 26, mismatch: 4, evidence_confidence: 74 },
      delta: 8.9, status: "rising", is_new: false, action: "test",
      evidence: ["解决长任务断点问题", "本地文件工作流简单", "可跨项目复用"],
      caveats: ["交接文件可能意外包含敏感上下文"]
    },
    {
      id: "unknown/one-click-growth", name: "One-click Growth", author: "Unknown", source: "directory",
      url: "https://agentskills.to/", purpose: "自动获取客户并批量发送营销消息",
      description: "宣称一键增长，但请求广泛账号权限并包含不透明的远程执行步骤。",
      scores: { fit: 88, demand: 86, leverage: 90, quality: 35, momentum: 92, maintenance: 38, uniqueness: 55, permissions: 92, execution: 88, network: 94, secrets: 96, obfuscation: 85, provenance: 90, mismatch: 72, evidence_confidence: 82 },
      delta: 31.2, status: "rising", is_new: true, action: "quarantine", hard_gate: true,
      evidence: ["目录热度快速上升", "作者身份和代码来源无法核验"],
      caveats: ["请求邮件与 CRM 凭据", "远程脚本内容不透明", "不得安装或执行"]
    }
  ],
  gaps: [
    { title: "中文企业信息核验", reason: "需求强，但现有方案在工商数据、来源标注和时效性上不稳定。", score: 86 },
    { title: "Skill 安全沙箱评测", reason: "市场增长快，真正做到权限最小化与行为复现的工具仍少。", score: 82 },
    { title: "跨平台 Skill 兼容层", reason: "同一工作流在 Codex、Claude 与其他 Agent 间仍需手工适配。", score: 74 }
  ]
};

let state = loadState() || structuredClone(demoData);
let activeTab = "all";
let selectedId = state.candidates[0]?.id;
let service = { online: false, token: null, status: null };
let pendingInstallId = null;
let githubSearchResults = [];

function clamp(value) { return Math.max(0, Math.min(100, Number(value) || 0)); }
function weighted(scores, weights) {
  let sum = 0, total = 0;
  Object.entries(weights).forEach(([key, weight]) => {
    const value = scores?.[key];
    if (value !== null && value !== undefined && !Number.isNaN(Number(value))) {
      sum += clamp(value) * weight;
      total += weight;
    }
  });
  return total ? sum / total : 0;
}
function normalizeCandidate(candidate) {
  const scores = candidate.scores || {};
  const opportunity = candidate.radar?.opportunity ?? weighted(scores, OPPORTUNITY_WEIGHTS);
  const risk = candidate.radar?.risk ?? weighted(scores, RISK_WEIGHTS);
  const confidence = clamp(candidate.radar?.confidence ?? scores.evidence_confidence ?? 0);
  const value = candidate.radar?.value_score ?? clamp(opportunity * (.4 + .6 * confidence / 100) - .35 * risk);
  const rawAction = candidate.action || candidate.radar?.action || "";
  let action = rawAction;
  if (rawAction.includes("adopt")) action = "adopt";
  else if (rawAction.includes("test") || rawAction.includes("shortlist")) action = "test";
  else if (rawAction.includes("watch")) action = "watch";
  else if (rawAction.includes("build")) action = "build";
  else if (rawAction.includes("quarantine") || candidate.hard_gate) action = "quarantine";
  else action = value >= 75 && risk < 30 && confidence >= 70 ? "adopt" : value >= 60 ? "test" : value >= 40 ? "watch" : "build";
  return {
    ...candidate,
    name: candidate.name || candidate.id || "未命名 Skill",
    author: candidate.author || candidate.id?.split("/")[0] || "未知作者",
    purpose: candidate.purpose || candidate.description || "暂无用途说明",
    description: candidate.description || candidate.purpose || "暂无详细说明。",
    source: candidate.source || "github",
    category: candidate.category || "未分类",
    platforms: Array.isArray(candidate.platforms) && candidate.platforms.length ? candidate.platforms : ["通用 SKILL.md"],
    history: Array.isArray(candidate.history) ? candidate.history : [],
    update_status: candidate.update_status || (candidate.updated_since_last ? "updated" : "unknown"),
    updated_since_last: Boolean(candidate.updated_since_last),
    delta: Number(candidate.delta ?? 0),
    status: candidate.status || (Number(candidate.delta) > 5 ? "rising" : Number(candidate.delta) < -3 ? "cooling" : "stable"),
    is_new: Boolean(candidate.is_new),
    action,
    evidence: candidate.evidence || [],
    caveats: candidate.caveats || [],
    radar: { opportunity, confidence, risk, value_score: value }
  };
}
function normalizeData(data) {
  const candidates = Array.isArray(data) ? data : data.candidates;
  if (!Array.isArray(candidates)) throw new Error("没有找到 candidates 数组");
  return {
    meta: Array.isArray(data) ? { observed_at: new Date().toISOString(), baseline: true } : (data.meta || { observed_at: new Date().toISOString(), baseline: true }),
    candidates: candidates.map(normalizeCandidate),
    gaps: Array.isArray(data.gaps) ? data.gaps : inferGaps(candidates.map(normalizeCandidate))
  };
}
function inferGaps(candidates) {
  return candidates.filter(x => x.action === "build").slice(0, 3).map(x => ({
    title: `${x.name} 的更安全替代`,
    reason: `${x.purpose} 有需求，但当前候选在质量、差异化或风险上仍有缺口。`,
    score: Math.round(x.radar.opportunity)
  }));
}
function saveState() {
  try { localStorage.setItem("skill-radar-state", JSON.stringify(state)); } catch (_) {}
}
function loadState() {
  try {
    const saved = localStorage.getItem("skill-radar-state");
    return saved ? normalizeData(JSON.parse(saved)) : null;
  } catch (_) { return null; }
}
function el(id) { return document.getElementById(id); }
function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function formatDate(value) {
  if (!value) return "未记录时间";
  try { return new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value)); }
  catch (_) { return String(value); }
}
function actionLabel(action) {
  return { adopt: "优先采用", test: "沙箱测试", watch: "继续观察", build: "开发替代", quarantine: "隔离" }[action] || "待评估";
}
function riskMeta(risk) {
  if (risk >= 60) return ["高风险", "risk-high"];
  if (risk >= 30) return ["中风险", "risk-mid"];
  return ["低风险", "risk-low"];
}
function sourceLabel(source) {
  return { official: "官方", directory: "目录", github: "GitHub", community: "社区" }[source] || source;
}

function render() {
  state = normalizeData(state);
  const list = state.candidates;
  if (!selectedId || !list.some(x => x.id === selectedId)) selectedId = list[0]?.id;
  const avg = list.length ? list.reduce((s, x) => s + x.radar.value_score, 0) / list.length : 0;
  el("totalKpi").textContent = list.length;
  el("newKpi").textContent = list.filter(x => x.is_new).length;
  el("risingKpi").textContent = list.filter(x => x.status === "rising").length;
  el("avgKpi").textContent = Math.round(avg);
  el("watchCount").textContent = list.filter(x => ["watch", "test"].includes(x.action)).length;
  el("riskCount").textContent = `${list.filter(x => x.radar.risk >= 60 || x.action === "quarantine").length} 个高风险候选`;
  el("updatedAt").textContent = state.meta?.baseline ? "首次基线" : `更新于 ${formatDate(state.meta?.observed_at)}`;
  el("footerMeta").textContent = `${formatDate(state.meta?.observed_at)} · ${state.meta?.window_days || 30} 天窗口`;
  renderSparks();
  renderRadarOptions();
  renderRadar();
  renderSignals();
  renderHistory();
  renderFilterOptions();
  renderTable();
  renderGaps();
  renderPrompt();
  renderService();
}

function renderSparks() {
  const items = [
    ["totalSpark", [4,8,7,12,11,16,18], "#37a7ff"],
    ["newSpark", [3,4,3,8,6,11,14], "#31d9aa"],
    ["riseSpark", [2,6,4,9,8,13,18], "#ffb84a"],
    ["avgSpark", [8,7,10,9,12,13,15], "#a685ff"]
  ];
  items.forEach(([id, values, color]) => {
    const max = Math.max(...values), min = Math.min(...values);
    const points = values.map((v, i) => `${i * 8},${22 - ((v - min) / Math.max(1, max - min)) * 18}`).join(" ");
    el(id).innerHTML = `<svg viewBox="0 0 48 24" aria-hidden="true"><polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.8"/><circle cx="48" cy="${points.split(" ").at(-1).split(",")[1]}" r="2" fill="${color}"/></svg>`;
  });
}
function renderRadarOptions() {
  el("radarSelect").innerHTML = state.candidates
    .sort((a,b) => b.radar.value_score - a.radar.value_score)
    .map(x => `<option value="${escapeHtml(x.id)}" ${x.id === selectedId ? "selected" : ""}>${escapeHtml(x.name)}</option>`).join("");
}
function polygonPoints(values, radius, cx, cy) {
  return values.map((value, i) => {
    const angle = -Math.PI / 2 + i * Math.PI * 2 / values.length;
    const r = radius * value / 100;
    return [cx + Math.cos(angle) * r, cy + Math.sin(angle) * r];
  });
}
function renderRadar() {
  const skill = state.candidates.find(x => x.id === selectedId);
  if (!skill) { el("radarChart").innerHTML = ""; return; }
  const keys = Object.keys(OPPORTUNITY_WEIGHTS).filter(key => skill.scores?.[key] != null);
  const cx = 210, cy = 167, radius = 122;
  let svg = "";
  [20,40,60,80,100].forEach(level => {
    svg += `<polygon class="radar-grid" points="${polygonPoints(keys.map(() => level), radius, cx, cy).map(p => p.join(",")).join(" ")}"/>`;
  });
  keys.forEach((key, i) => {
    const [x, y] = polygonPoints(keys.map((_, j) => i === j ? 100 : 0), radius, cx, cy)[i];
    const [lx, ly] = polygonPoints(keys.map((_, j) => i === j ? 122 : 0), radius, cx, cy)[i];
    svg += `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"/>`;
    svg += `<text class="radar-label" x="${lx}" y="${ly + 3}">${LABELS[key]}</text>`;
  });
  const values = keys.map(k => clamp(skill.scores?.[k]));
  const points = polygonPoints(values, radius, cx, cy);
  svg += `<polygon class="radar-shape" points="${points.map(p => p.join(",")).join(" ")}"/>`;
  points.forEach(([x,y]) => svg += `<circle class="radar-point" cx="${x}" cy="${y}" r="3"/>`);
  el("radarChart").innerHTML = svg;
  el("radarScore").textContent = Math.round(skill.radar.value_score);
  el("radarAction").textContent = actionLabel(skill.action);
  el("radarAction").style.color = skill.action === "quarantine" ? "var(--red)" : skill.action === "watch" ? "var(--amber)" : "var(--mint)";
}
function renderSignals() {
  const list = state.candidates;
  const signals = [
    ["高价值候选", list.filter(x => x.radar.value_score >= 65).length],
    ["低风险候选", list.filter(x => x.radar.risk < 30).length],
    ["GitHub 升温", list.filter(x => (x.github_signal?.star_delta || 0) > 0).length],
    ["X 热度可用", list.filter(x => x.scores?.x_heat != null).length]
  ];
  const max = Math.max(1, list.length);
  el("signalStack").innerHTML = signals.map(([label, count]) =>
    `<div class="signal-row"><label>${label}</label><div class="signal-track"><i style="width:${count/max*100}%"></i></div><b>${count}</b></div>`
  ).join("");
}
function renderFilterOptions() {
  const configs = [
    ["categoryFilter", [...new Set(state.candidates.map(x => x.category).filter(Boolean))].sort()],
    ["platformFilter", [...new Set(state.candidates.flatMap(x => x.platforms || []).filter(Boolean))].sort()]
  ];
  configs.forEach(([id, values]) => {
    const select = el(id);
    const current = select.value || "all";
    const label = id === "categoryFilter" ? "全部领域" : "全部平台";
    select.innerHTML = `<option value="all">${label}</option>${values.map(value =>
      `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    ).join("")}`;
    select.value = values.includes(current) ? current : "all";
  });
}
function renderHistory() {
  const skill = state.candidates.find(x => x.id === selectedId);
  const history = (skill?.history || []).filter(point => point?.value != null).slice(-30);
  const svg = el("historyChart");
  const empty = el("historyEmpty");
  const updates = state.candidates.filter(x => x.updated_since_last);
  el("updateSummary").textContent = `${updates.length} 个 Skill 检测到新版本 · 保留最近 30 次观测`;
  el("updateFeed").innerHTML = updates.length
    ? updates.slice(0, 5).map(x => `<button class="update-item" data-detail="${escapeHtml(x.id)}">
        <span class="update-dot"></span><span><strong>${escapeHtml(x.name)}</strong><small>${escapeHtml(x.version_label || "新修订")} · ${formatDate(x.last_skill_update_at)}</small></span><em>查看 →</em>
      </button>`).join("")
    : `<div class="update-placeholder"><strong>本期没有内容变更</strong><p>版本检测只比较 Skill 内容指纹，不会把仓库中无关文件的变化误报为新版本。</p></div>`;
  if (!history.length) {
    svg.innerHTML = "";
    empty.hidden = false;
    return;
  }
  empty.hidden = history.length >= 2;
  const width = 640, height = 210, left = 36, right = 18, top = 20, bottom = 30;
  const plotW = width - left - right, plotH = height - top - bottom;
  const xAt = index => left + (history.length === 1 ? plotW / 2 : index * plotW / (history.length - 1));
  const yAt = value => top + (100 - clamp(value)) / 100 * plotH;
  let markup = "";
  [0, 25, 50, 75, 100].forEach(value => {
    const y = yAt(value);
    markup += `<line class="history-grid-line" x1="${left}" y1="${y}" x2="${width-right}" y2="${y}"/><text class="history-axis-label" x="4" y="${y+3}">${value}</text>`;
  });
  const valuePoints = history.map((point, index) => `${xAt(index)},${yAt(point.value)}`).join(" ");
  const riskPoints = history.map((point, index) => `${xAt(index)},${yAt(point.risk ?? 0)}`).join(" ");
  markup += `<polyline class="history-value-line" points="${valuePoints}"/><polyline class="history-risk-line" points="${riskPoints}"/>`;
  history.forEach((point, index) => {
    const label = point.observed_at ? String(point.observed_at).slice(5,10) : `#${index+1}`;
    markup += `<circle class="history-value-point" cx="${xAt(index)}" cy="${yAt(point.value)}" r="3"><title>${label} 价值 ${Math.round(point.value)}</title></circle>`;
    if (index === 0 || index === history.length - 1) markup += `<text class="history-date-label" x="${xAt(index)}" y="${height-7}">${label}</text>`;
  });
  svg.innerHTML = markup;
}
function activeSources() {
  return [...document.querySelectorAll("[data-source]:checked")].map(x => x.dataset.source);
}
function filteredCandidates() {
  const query = el("searchInput").value.trim().toLowerCase();
  const action = el("actionFilter").value;
  const category = el("categoryFilter").value;
  const platform = el("platformFilter").value;
  const valueRange = el("valueFilter").value;
  const [valueMin, valueMax] = valueRange === "all" ? [0, 100] : valueRange.split("-").map(Number);
  const sources = activeSources();
  return state.candidates.filter(x => {
    const text = `${x.name} ${x.author} ${x.purpose} ${x.description} ${x.repo || ""} ${x.category} ${(x.platforms || []).join(" ")}`.toLowerCase();
    const tabMatch = activeTab === "all" || (activeTab === "new" && x.is_new) || (activeTab === "rising" && x.status === "rising") || (activeTab === "updated" && x.updated_since_last) || (activeTab === "safe" && x.radar.risk < 30);
    const valueMatch = x.radar.value_score >= valueMin && x.radar.value_score <= valueMax;
    return sources.includes(x.source) && tabMatch && valueMatch
      && (action === "all" || x.action === action)
      && (category === "all" || x.category === category)
      && (platform === "all" || (x.platforms || []).includes(platform))
      && (!query || text.includes(query));
  }).sort((a,b) => b.radar.value_score - a.radar.value_score);
}
function renderTable() {
  const list = filteredCandidates();
  el("rankingBody").innerHTML = list.map((x, index) => {
    const [riskLabel, riskClass] = riskMeta(x.radar.risk);
    const ghHeat = x.scores?.github_heat == null ? "—" : Math.round(x.scores.github_heat);
    const xHeat = x.scores?.x_heat == null ? "—" : Math.round(x.scores.x_heat);
    return `<tr>
      <td class="rank">${String(index + 1).padStart(2, "0")}</td>
      <td><div class="skill-cell"><span class="skill-avatar">${escapeHtml(x.name.slice(0,2).toUpperCase())}</span><div><strong>${escapeHtml(x.name)}</strong><small>${escapeHtml(x.author)} · ${sourceLabel(x.source)}</small></div></div></td>
      <td><div class="purpose-cell">${escapeHtml(x.purpose)}<small>${escapeHtml(x.category)} · ${escapeHtml((x.platforms || ["通用 SKILL.md"]).slice(0,2).join(" / "))}${x.updated_since_last ? ' · <b>新版本</b>' : ""}</small></div></td>
      <td><div class="score-ring" style="--score:${x.radar.value_score}">${Math.round(x.radar.value_score)}</div></td>
      <td><div class="heat-pair"><span>GH <b>${ghHeat}</b></span><span>X <b>${xHeat}</b></span></div></td>
      <td><span class="risk-pill ${riskClass}">● ${riskLabel}</span></td>
      <td><span class="action-pill action-${x.action}">${actionLabel(x.action)}</span></td>
      <td><button class="more-btn" data-detail="${escapeHtml(x.id)}" aria-label="查看 ${escapeHtml(x.name)} 详情">→</button></td>
    </tr>`;
  }).join("");
  el("emptyState").hidden = list.length > 0;
}
function renderGaps() {
  const gaps = state.gaps?.length ? state.gaps : [{ title: "暂无明确空白", reason: "扩大扫描范围或积累第二期快照后再判断。", score: 0 }];
  el("gapList").innerHTML = gaps.slice(0, 3).map(x =>
    `<div class="gap-item"><div><strong>${escapeHtml(x.title)}</strong><p>${escapeHtml(x.reason)}</p></div><span>机会 ${Math.round(x.score || 0)}</span></div>`
  ).join("");
}
function renderPrompt() {
  const sourceNames = activeSources().map(sourceLabel).join("、");
  el("promptText").textContent = `使用 $skill-radar，扫描过去 30 天的${sourceNames}，验证并评分 20 个候选，输出前 5 名、风险隔离项、开发空白，并生成可导入网页的 JSON 快照。`;
}
function renderService() {
  const dot = el("serviceDot");
  dot.className = service.online ? "online" : "offline";
  el("serviceLabel").textContent = service.online ? "联网服务已连接" : "当前为静态模式";
  el("serviceText").textContent = service.online
    ? `数据源联网可用 · ${service.status?.refreshing ? "正在更新" : "等待指令"}`
    : "请双击“启动联网版.cmd”，再从 http://127.0.0.1:8765 打开";
  el("refreshOnline").disabled = !service.online || service.status?.refreshing;
  el("openGithubSearch").disabled = !service.online;
  el("refreshOnline").innerHTML = service.status?.refreshing ? "<span>↻</span> 正在扫描…" : "<span>↻</span> 立即联网更新";
  el("scheduleBtn").disabled = !service.online;
  el("scheduleBtn").classList.toggle("active", Boolean(service.status?.daily_task_installed));
  el("scheduleBtn").textContent = service.status?.daily_task_installed ? "每日任务已启用" : "启用每日任务";
  el("nextRefresh").textContent = service.online
    ? (service.status?.daily_task_installed
      ? `每天 ${service.status?.daily_time || "08:00"} 自动更新`
      : "服务运行期间每 24 小时更新")
    : "联网、安装和每日任务不可用";
  el("sourceHealth").innerHTML = service.online
    ? `<span>联网源</span><strong>${state.meta?.sources_scanned || 0} 个仓库 · ${state.meta?.updated_skills || 0} 个更新 · X ${state.meta?.x_status === "ok" ? `${state.meta?.x_enriched || 0} 项` : "未配置"} · ${state.meta?.errors?.length || 0} 个异常</strong>`
    : "<span>联网源</span><strong>等待本地服务</strong>";
  if (service.status) {
    el("codexPath").textContent = service.status.codex_path || "~/.codex/skills";
    el("hermesPath").textContent = service.status.hermes_path || "~/.hermes/skills";
  }
}

async function connectService() {
  try {
    const sessionResponse = await fetch("/api/session", { cache: "no-store" });
    if (!sessionResponse.ok) throw new Error("service unavailable");
    const session = await sessionResponse.json();
    service.token = session.token;
    service.online = true;
    const [statusResponse, snapshotResponse] = await Promise.all([
      fetch("/api/status", { cache: "no-store" }),
      fetch("/api/snapshot", { cache: "no-store" })
    ]);
    if (statusResponse.ok) service.status = await statusResponse.json();
    if (snapshotResponse.ok) {
      state = normalizeData(await snapshotResponse.json());
      selectedId = state.candidates[0]?.id;
      saveState();
    }
  } catch (_) {
    service = { online: false, token: null, status: null };
    try {
      const publicSnapshot = await fetch("data/current.json", { cache: "no-store" });
      if (publicSnapshot.ok) {
        state = normalizeData(await publicSnapshot.json());
        selectedId = state.candidates[0]?.id;
        saveState();
      }
    } catch (_) {}
  }
  render();
}

async function apiPost(path, payload) {
  if (!service.online || !service.token) throw new Error("联网服务尚未启动");
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Radar-Token": service.token },
    body: JSON.stringify(payload)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `请求失败：HTTP ${response.status}`);
  return data;
}

async function refreshOnline() {
  if (!service.online) return toast("请先启动联网版");
  service.status = { ...(service.status || {}), refreshing: true };
  renderService();
  try {
    const result = await apiPost("/api/refresh", {});
    state = normalizeData(result.snapshot);
    selectedId = state.candidates[0]?.id;
    saveState();
    service.status = { ...(service.status || {}), refreshing: false, last_refresh: state.meta?.observed_at };
    render();
    toast(`联网更新完成：${state.candidates.length} 个候选`);
  } catch (error) {
    service.status = { ...(service.status || {}), refreshing: false };
    renderService();
    toast(error.message);
  }
}

async function toggleSchedule() {
  if (!service.online) return toast("请先启动联网版");
  const enabled = !service.status?.daily_task_installed;
  if (enabled && !window.confirm("将创建 Windows 每日任务，每天 08:00 联网更新 Skill Radar。是否继续？")) return;
  if (!enabled && !window.confirm("将删除 Skill Radar 的 Windows 每日更新任务。是否继续？")) return;
  try {
    const result = await apiPost("/api/schedule", { enabled, time: "08:00" });
    service.status = { ...(service.status || {}), daily_task_installed: result.enabled, daily_time: result.time || "08:00" };
    renderService();
    toast(result.enabled ? "每日更新任务已启用" : "每日更新任务已关闭");
  } catch (error) { toast(error.message); }
}
function openGithubSearch() {
  el("githubSearchModal").hidden = false;
  el("githubSearchStatus").textContent = service.online
    ? "仅搜索公开 GitHub 仓库；结果不会自动安装。"
    : "请先启动本地联网版，再使用 GitHub 搜索。";
  el("runGithubSearch").disabled = !service.online;
  setTimeout(() => el("githubQuery").focus(), 20);
}
function closeGithubSearch() {
  el("githubSearchModal").hidden = true;
}
function renderGithubResults() {
  if (!githubSearchResults.length) {
    el("githubResults").innerHTML = '<div class="github-empty">暂无匹配结果。可以换一个更具体的英文任务词，例如 pdf、research、seo。</div>';
    return;
  }
  el("githubResults").innerHTML = githubSearchResults.map(x => {
    const [riskLabel, riskClass] = riskMeta(x.radar.risk);
    const alreadyAdded = state.candidates.some(item => item.id === x.id);
    return `<article class="github-result">
      <div class="github-result-main">
        <div class="github-result-head"><strong>${escapeHtml(x.name)}</strong><span>${escapeHtml(x.category)}</span></div>
        <p>${escapeHtml(x.explanation_cn?.summary_cn || x.purpose)}</p>
        <div class="github-result-meta">
          <span>${escapeHtml(x.repo || x.author)}</span>
          <span>★ ${Number(x.repo_stars || 0).toLocaleString()}</span>
          <span>价值 ${Math.round(x.radar.value_score)}</span>
          <span class="${riskClass}">${riskLabel}</span>
          <span>${escapeHtml((x.platforms || ["通用 SKILL.md"]).slice(0,3).join(" / "))}</span>
        </div>
      </div>
      <div class="github-result-actions">
        <button class="btn ${alreadyAdded ? "ghost" : "primary"}" data-add-search="${escapeHtml(x.id)}" ${alreadyAdded ? "disabled" : ""}>${alreadyAdded ? "已在雷达" : "加入雷达"}</button>
        <a href="${escapeHtml(x.url || "#")}" target="_blank" rel="noreferrer">查看 GitHub ↗</a>
      </div>
    </article>`;
  }).join("");
}
async function runGithubSearch() {
  const query = el("githubQuery").value.trim();
  if (query.length < 2) {
    el("githubSearchStatus").textContent = "请输入至少 2 个字符的关键词。";
    return;
  }
  const button = el("runGithubSearch");
  button.disabled = true;
  button.textContent = "搜索中…";
  el("githubSearchStatus").textContent = "正在检索 GitHub 仓库并核验 SKILL.md，通常需要 10–30 秒…";
  el("githubResults").innerHTML = "";
  try {
    const result = await apiPost("/api/search-github", { query, limit: 12 });
    githubSearchResults = (result.candidates || []).map(normalizeCandidate);
    el("githubSearchStatus").textContent = `已搜索 ${result.searched_repos || 0} 个仓库，找到 ${githubSearchResults.length} 个匹配 Skill${result.errors?.length ? `；${result.errors.length} 个源暂不可用` : ""}。`;
    renderGithubResults();
  } catch (error) {
    githubSearchResults = [];
    el("githubSearchStatus").textContent = `搜索失败：${error.message}`;
    el("githubResults").innerHTML = '<div class="github-empty">如果提示 GitHub 限流，请稍后重试或为本地服务配置 GITHUB_TOKEN。</div>';
  } finally {
    button.disabled = false;
    button.textContent = "搜索";
  }
}
function addGithubResult(id) {
  const candidate = githubSearchResults.find(item => item.id === id);
  if (!candidate || state.candidates.some(item => item.id === id)) return;
  state.candidates = [candidate, ...state.candidates];
  state.meta = { ...(state.meta || {}), manual_github_results: Number(state.meta?.manual_github_results || 0) + 1 };
  selectedId = candidate.id;
  saveState();
  render();
  renderGithubResults();
  toast(`已加入雷达：${candidate.name}`);
}
function openDrawer(id) {
  const x = state.candidates.find(item => item.id === id);
  if (!x) return;
  selectedId = id;
  el("radarSelect").value = id;
  renderRadar();
  renderHistory();
  const [riskLabel, riskClass] = riskMeta(x.radar.risk);
  const bars = Object.keys(OPPORTUNITY_WEIGHTS).filter(k => x.scores?.[k] != null).map(k =>
    `<div class="score-bar"><span>${LABELS[k]}</span><i style="--value:${clamp(x.scores?.[k])}"></i><b>${Math.round(clamp(x.scores?.[k]))}</b></div>`
  ).join("");
  const cn = x.explanation_cn || {
    summary_cn: x.description,
    best_for_cn: "希望把重复任务标准化的个人或团队",
    how_it_works_cn: "通过 SKILL.md 为 Agent 提供可复用工作流。",
    typical_use_cn: x.purpose
  };
  const installDisabled = !service.online || !x.repo || x.action === "quarantine";
  el("drawerContent").innerHTML = `
    <div class="drawer-hero">
      <span class="skill-avatar">${escapeHtml(x.name.slice(0,2).toUpperCase())}</span>
      <p class="eyebrow">${sourceLabel(x.source)} · ${escapeHtml(x.author)}</p>
      <h2>${escapeHtml(x.name)}</h2>
      ${x.url ? `<a class="drawer-url" href="${escapeHtml(x.url)}" target="_blank" rel="noreferrer">${escapeHtml(x.url)}</a>` : ""}
      <p class="drawer-desc">${escapeHtml(cn.summary_cn || x.description)}</p>
      <span class="action-pill action-${x.action}">${actionLabel(x.action)}</span>
    </div>
    <div class="drawer-grid">
      <div class="mini-stat"><span>价值</span><strong>${Math.round(x.radar.value_score)}</strong></div>
      <div class="mini-stat"><span>置信度</span><strong>${Math.round(x.radar.confidence)}</strong></div>
      <div class="mini-stat"><span class="${riskClass}">风险</span><strong>${Math.round(x.radar.risk)}</strong></div>
    </div>
    <section class="detail-section">
      <h3>中文详情解释</h3>
      <div class="cn-detail">
        <strong>它是什么</strong><p>${escapeHtml(cn.summary_cn || x.description)}</p>
        <strong>适合谁</strong><p>${escapeHtml(cn.best_for_cn || "暂无明确说明")}</p>
        <strong>怎么工作</strong><p>${escapeHtml(cn.how_it_works_cn || "暂无明确说明")}</p>
        <strong>什么时候用</strong><p>${escapeHtml(cn.typical_use_cn || x.purpose)}</p>
      </div>
    </section>
    <section class="detail-section"><h3>价值维度</h3><div class="score-bars">${bars}</div></section>
    <section class="detail-section">
      <h3>社区热度证据</h3>
      <div class="cn-detail">
        <strong>GitHub</strong><p>累计 Stars：${Number(x.github_signal?.stars ?? x.repo_stars ?? 0).toLocaleString()}；本期新增：${x.github_signal?.star_delta == null ? "首次基线" : `+${x.github_signal.star_delta}`}；热度分：${x.scores?.github_heat == null ? "未知" : Math.round(x.scores.github_heat)}。</p>
        <strong>X / Twitter（最近 7 天）</strong><p>${x.x_signal?.status === "ok" ? `提及 ${x.x_signal.posts} 条、独立作者 ${x.x_signal.authors} 位、综合互动 ${x.x_signal.engagement}，热度分 ${Math.round(x.scores.x_heat)}。` : "暂无可信 API 数据，当前评分未把 X 热度按 0 分处理。"}</p>
      </div>
    </section>
    <section class="detail-section">
      <h3>版本与兼容性</h3>
      <div class="cn-detail">
        <strong>当前修订</strong><p>${escapeHtml(x.version_label || "尚未建立内容指纹")}${x.updated_since_last ? "；本期检测到新版本。" : "；本期未检测到内容变化。"}</p>
        <strong>兼容平台</strong><p>${escapeHtml((x.platforms || ["通用 SKILL.md"]).join("、"))}</p>
        <strong>变更摘要</strong><p>${x.change_summary?.length ? x.change_summary.map(escapeHtml).join("；") : "暂无需要提醒的内容变化。"}</p>
      </div>
    </section>
    <section class="detail-section"><h3>关键证据</h3>${x.evidence.length ? `<ul>${x.evidence.map(v => `<li>${escapeHtml(typeof v === "string" ? v : v.claim || JSON.stringify(v))}</li>`).join("")}</ul>` : "<p>尚未记录结构化证据。</p>"}</section>
    <section class="detail-section"><h3>注意事项</h3>${x.caveats.length ? `<ul>${x.caveats.map(v => `<li>${escapeHtml(v)}</li>`).join("")}</ul>` : `<p><span class="risk-pill ${riskClass}">${riskLabel}</span> 暂无额外说明。</p>`}</section>
    <div class="drawer-install">
      <button class="btn primary" data-install="${escapeHtml(x.id)}" data-target="codex" ${installDisabled ? "disabled" : ""}>安装到 Codex</button>
      <button class="btn ghost" data-install="${escapeHtml(x.id)}" data-target="hermes" ${installDisabled ? "disabled" : ""}>安装到 Hermes</button>
      <button class="btn ghost portable-export" data-package-export="${escapeHtml(x.id)}" ${installDisabled ? "disabled" : ""}>导出通用 Skill 包</button>
    </div>
    ${x.action === "quarantine" ? '<p class="form-error">该候选触发安全隔离，已禁止一键安装。</p>' : !service.online ? '<p class="form-error">启动联网版后才能安装。</p>' : ""}`;
  el("drawerBackdrop").hidden = false;
  el("detailDrawer").classList.add("open");
  el("detailDrawer").setAttribute("aria-hidden", "false");
}

function openInstall(id, target) {
  const x = state.candidates.find(item => item.id === id);
  if (!x || !service.online) return toast("请先启动联网版");
  pendingInstallId = id;
  document.querySelectorAll('input[name="installTarget"]').forEach(input => { input.checked = input.value === target; });
  el("installSummary").innerHTML = `<strong>${escapeHtml(x.name)}</strong><p>${escapeHtml(x.explanation_cn?.summary_cn || x.purpose)}</p><p>价值 ${Math.round(x.radar.value_score)} · 风险 ${Math.round(x.radar.risk)} · 来源 ${escapeHtml(x.repo || x.author)}</p>`;
  el("installConfirm").checked = false;
  el("applyInstall").disabled = true;
  el("installError").textContent = "";
  el("installModal").hidden = false;
}
function closeInstall() {
  el("installModal").hidden = true;
  pendingInstallId = null;
}
async function applyInstall() {
  if (!pendingInstallId || !el("installConfirm").checked) return;
  const target = document.querySelector('input[name="installTarget"]:checked')?.value;
  el("applyInstall").disabled = true;
  el("applyInstall").textContent = "正在安全安装…";
  el("installError").textContent = "";
  try {
    const result = await apiPost("/api/install", { id: pendingInstallId, target, confirm: true });
    closeInstall();
    toast(`安装完成：${result.path}${result.restart_required ? "；请重启 Codex" : ""}`);
  } catch (error) {
    el("installError").textContent = error.message;
  } finally {
    el("applyInstall").textContent = "确认安装";
    el("applyInstall").disabled = !el("installConfirm").checked;
  }
}
async function exportPortable(id) {
  if (!service.online) return toast("启动联网版后才能导出完整 Skill 包");
  const button = document.querySelector(`[data-package-export="${CSS.escape(id)}"]`);
  if (button) { button.disabled = true; button.textContent = "正在打包…"; }
  try {
    const result = await apiPost("/api/export", { id });
    const binary = atob(result.content_base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
    const url = URL.createObjectURL(new Blob([bytes], { type: "application/zip" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = result.filename || "skill-portable.zip";
    link.click();
    URL.revokeObjectURL(url);
    toast("通用 Skill 包已导出");
  } catch (error) {
    toast(`导出失败：${error.message}`);
  } finally {
    if (button) { button.disabled = false; button.textContent = "导出通用 Skill 包"; }
  }
}
function closeDrawer() {
  el("detailDrawer").classList.remove("open");
  el("detailDrawer").setAttribute("aria-hidden", "true");
  setTimeout(() => el("drawerBackdrop").hidden = true, 220);
}
function openImport() {
  el("importModal").hidden = false;
  el("importError").textContent = "";
  setTimeout(() => el("jsonInput").focus(), 20);
}
function closeImport() { el("importModal").hidden = true; }
function applyData(raw) {
  state = normalizeData(raw);
  state.meta.demo = false;
  selectedId = state.candidates[0]?.id;
  saveState();
  render();
  closeImport();
  toast(`已载入 ${state.candidates.length} 个候选`);
}
function exportData() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `skill-radar-${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  toast("快照已导出");
}
function toast(message) {
  el("toast").textContent = message;
  el("toast").classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el("toast").classList.remove("show"), 1800);
}

document.addEventListener("click", event => {
  const detail = event.target.closest("[data-detail]");
  if (detail) openDrawer(detail.dataset.detail);
  const install = event.target.closest("[data-install]");
  if (install) openInstall(install.dataset.install, install.dataset.target);
  const packageExport = event.target.closest("[data-package-export]");
  if (packageExport) exportPortable(packageExport.dataset.packageExport);
  const addSearch = event.target.closest("[data-add-search]");
  if (addSearch) addGithubResult(addSearch.dataset.addSearch);
});
document.querySelectorAll(".tab").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  button.classList.add("active");
  activeTab = button.dataset.tab;
  renderTable();
}));
document.querySelectorAll("[data-source]").forEach(input => input.addEventListener("change", () => { renderTable(); renderPrompt(); }));
document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
  button.classList.add("active");
  const target = button.dataset.view === "gaps" ? ".bottom-grid" : button.dataset.view === "watchlist" ? ".ranking-panel" : ".topbar";
  document.querySelector(target)?.scrollIntoView({ behavior: "smooth", block: "start" });
  if (button.dataset.view === "watchlist") { el("actionFilter").value = "watch"; renderTable(); }
}));
el("radarSelect").addEventListener("change", e => { selectedId = e.target.value; renderRadar(); renderHistory(); });
el("searchInput").addEventListener("input", renderTable);
el("actionFilter").addEventListener("change", renderTable);
el("categoryFilter").addEventListener("change", renderTable);
el("platformFilter").addEventListener("change", renderTable);
el("valueFilter").addEventListener("change", renderTable);
el("resetFilters").addEventListener("click", () => {
  el("searchInput").value = "";
  ["actionFilter", "categoryFilter", "platformFilter", "valueFilter"].forEach(id => { el(id).value = "all"; });
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("active", x.dataset.tab === "all"));
  activeTab = "all";
  renderTable();
});
el("showRisk").addEventListener("click", () => { el("actionFilter").value = "quarantine"; renderTable(); document.querySelector(".ranking-panel").scrollIntoView({ behavior: "smooth" }); });
el("openImport").addEventListener("click", openImport);
el("openGithubSearch").addEventListener("click", openGithubSearch);
el("closeGithubSearch").addEventListener("click", closeGithubSearch);
el("githubSearchModal").addEventListener("click", e => { if (e.target === el("githubSearchModal")) closeGithubSearch(); });
el("runGithubSearch").addEventListener("click", runGithubSearch);
el("githubQuery").addEventListener("keydown", e => { if (e.key === "Enter") runGithubSearch(); });
el("closeImport").addEventListener("click", closeImport);
el("importModal").addEventListener("click", e => { if (e.target === el("importModal")) closeImport(); });
el("applyImport").addEventListener("click", () => {
  try {
    const text = el("jsonInput").value.trim();
    if (!text) throw new Error("请先选择文件或粘贴 JSON");
    applyData(JSON.parse(text));
  } catch (error) { el("importError").textContent = `无法导入：${error.message}`; }
});
el("fileInput").addEventListener("change", async e => {
  const file = e.target.files?.[0];
  if (!file) return;
  el("jsonInput").value = await file.text();
  el("importError").textContent = "";
});
el("loadDemo").addEventListener("click", () => {
  state = structuredClone(demoData);
  try { localStorage.removeItem("skill-radar-state"); } catch (_) {}
  selectedId = state.candidates[0].id;
  render();
  closeImport();
  toast("已恢复演示数据");
});
el("exportBtn").addEventListener("click", exportData);
el("refreshOnline").addEventListener("click", refreshOnline);
el("scheduleBtn").addEventListener("click", toggleSchedule);
el("closeDrawer").addEventListener("click", closeDrawer);
el("drawerBackdrop").addEventListener("click", closeDrawer);
el("closeInstall").addEventListener("click", closeInstall);
el("cancelInstall").addEventListener("click", closeInstall);
el("installModal").addEventListener("click", e => { if (e.target === el("installModal")) closeInstall(); });
el("installConfirm").addEventListener("change", e => { el("applyInstall").disabled = !e.target.checked; });
el("applyInstall").addEventListener("click", applyInstall);
el("copyPrompt").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(el("promptText").textContent); toast("扫描指令已复制"); }
  catch (_) { toast("请手动复制上方指令"); }
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") { closeDrawer(); closeImport(); closeInstall(); closeGithubSearch(); }
});

render();
connectService();
