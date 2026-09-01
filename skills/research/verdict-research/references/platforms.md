# Plataformas y Queries Optimizadas

## Reddit

###Subreddits técnicos comunes
r/python, r/javascript, r/rust, r/golang, r/programming, r/ExperiencedDevs,
r/cscareerquestions, r/programming, r/webdev, r/MachineLearning, r/LocalLLaMA,
r/selfhosted, r/devops, r/docker, r/kubernetes, r/dataengineering, r/SQL,
r/reactjs, r/vue, r/sveltejs, r/node, r/dotnet, r/java, r/cpp, r/csharp

### Queries efectivas
- `"TEMA" site:reddit.com` (general)
- `"TEMA" review OR experience OR honest site:reddit.com` (opiniones)
- `"TEMA" problem OR issue OR frustrating OR broken site:reddit.com` (problemas)
- `"TEMA" vs OR compared OR better site:reddit.com` (comparativas)
- `"TEMA" tip OR trick OR workaround OR undocumented site:reddit.com` (trucos)

### Acceso cuando la API falla
```bash
# old.reddit.com HTML scraping (HTTP 200 incluso cuando JSON API da 403)
curl -s -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
  'https://old.reddit.com/r/SUBREDDIT/search?q=QUERY&restrict_sr=on&sort=relevance&t=year'
```

---

## X/Twitter

### Queries efectivas
- `"TEMA" site:x.com` (general)
- `"TEMA" review OR thread OR opinion site:x.com` (opiniones)
- `"TEMA" from:USERNAME` (opinión de dev específico)
- `"TEMA" site:twitter.com` (fallback, resultados indexados)

### Limitación
X frecuentemente bloquea acceso no autenticado. Marcar snippets como INDIRECT.

---

## Facebook

### Queries efectivas
- `"TEMA" site:facebook.com/groups` (grupos públicos)
- `"TEMA" review OR experience site:facebook.com/groups` (opiniones en grupos)

### Limitación
La mayoría de grupos requieren login. Usar snippets indexados por search engines.

---

## YouTube

### Estrategia
1. Buscar videos de review/opinión sobre el tema con `web_search`
2. Extraer transcript con `youtube-content` skill — la opinión del creador ES data social
3. Buscar comentarios del video si están indexados

### Queries efectivas
- `"TEMA" review OR honest OR opinion site:youtube.com` (reviews)
- `"TEMA" tutorial OR explained OR deep dive site:youtube.com` (educativo)
- `"TEMA" is it worth it OR should you use site:youtube.com` (veredictos)

### Extracción de transcript
```bash
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only
```

---

## Discord

### Queries efectivas
- `"TEMA" site:discord.com` (servidores públicos indexados)
- `"TEMA" discord invite OR server` (invitaciones públicas)

### Limitación
Discord requiere estar dentro del server para leer mensajes. Buscar servidores
públicos que se mencionan en Reddit/foros sobre el tema.

---

## TikTok

### Queries effectivas
- `"TEMA" review OR honest site:tiktok.com` (limitado)
- `"TEMA" dev OR engineer OR programmer site:tiktok.com` (contenido técnico)

### Limitación
TikTok tiene SEO muy pobre. Usar como fuente complementaria de mínima.
Enfocarse en creadores técnicos conocidos que opinen sobre el tema.

---

## Hacker News

### Queries efectivas
- `"TEMA" site:news.ycombinator.com` (discusiones)
- `"TEMA" site:news.ycombinator.com` OR `TEMA "Hacker News"` (fallback)

### Valor
HN tiene discusiones técnicas profundas con ingenieros senior. Los comentarios
suelen ser de alto valor técnico. Frecuentemente incluyen anécdotas de producción.

---

## Stack Overflow

### Queries efectivas
- `"TEMA" site:stackoverflow.com` (preguntas/respuestas)
- `"TEMA" performance OR scalability OR production site:stackoverflow.com` (problemas reales)
- `"TEMA" best practice OR recommended site:stackoverflow.com` (recomendaciones)

### Valor
Problemas técnicos concretos con soluciones verificadas por upvotes de la comunidad.
Las preguntas con alta puntuación representan problemas reales y comunes.

---

## GitHub Issues / Discussions

### Queries efectivas
- `"TEMA" site:github.com issues` (bugs y problemas)
- `"TEMA" site:github.com discussions` (debates de diseño)
- `repo:owner/name TEMA` (búsqueda dentro de repo específico)

### Con gh CLI (si disponible)
```bash
gh issue list --repo OWNER/REPO --search "TEMA" --state all --limit 20
gh issue view NUMBER --repo OWNER/REPO --comments
```

---

## Foros especializados

### Dev.to
- `"TEMA" site:dev.to` (artículos de developers)
- `"TEMA" beginner OR experience OR opinion site:dev.to` (opiniones)

### Medium
- `"TEMA" site:medium.com engineering OR architecture` (deep dives técnicos)
- `"TEMA" site:medium.com review OR experience` (reviews)

### Blogs de ingeniería
- `"TEMA" engineering blog site:medium.com OR site:dev.to` (posts de ingenieros)
- `"TEMA" postmortem OR lessons learned` (post-mortems, muy valiosos)

---

## arXiv (académico)

### Cuando usarlo
Si el tema es científico, o cuando la comunidad discute conceptos algorítmicos/
teóricos, buscar papers que respalden o refuten claims.

### Queries efectivas
```bash
python3 scripts/search_arxiv.py "TEMA" --sort date --max 10
```

### Semantic Scholar (citations)
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=TEMA&limit=5&fields=title,authors,year,citationCount"
```
