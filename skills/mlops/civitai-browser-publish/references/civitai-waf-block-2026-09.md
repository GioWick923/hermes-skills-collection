# Civitai WAF Block - 2026-09-08

## Incidente
Chrome CDP (puerto 9222) bloqueado por WAF de Civitai al intentar publicar modelo "Ultra Dream Nexus".

## Señales
- Página muestra: "抱歉，您的访问疑似攻击请求，已被系统自动拦截，如为误封请联系客服。"
- Traducción: "Sorry, your access is suspected to be an attack request, automatically blocked by the system. If blocked by mistake, please contact customer service."
- HTTP status: 200 (la página carga pero con mensaje de bloqueo)

## Causa
Civitai detecta tráfico automatizado vía CDP y aplica WAF. El bloqueo es específico para:
- Conexiones desde `127.0.0.1:9222` (Chrome debugging port)
- User-Agent modificado por DevTools Protocol
- Patrones de automatización detectables

## Soluciones alternativas intentadas
1. **Chrome con perfil separado** → FALLÓ (mismo WAF)
2. **stealth-browser MCP** → FALLÓ (error de sandbox, no pudo iniciar)
3. **Brave** → No probado (mismo motor Chromium, probable mismo bloqueo)

## Recomendación futura
- Usar **publicación manual** como fallback principal
- Para automatización: considerar VPN/proxy o rotate User-Agent
- Monitorear si el bloqueo es temporal (puede levantarse en horas/días)

## Contexto técnico
- Cuenta: <CIVITAI_USER> (ID 2836482)
- Modelo bloqueado: `triultra_final_xtrio_50_35_15_fp32.safetensors` (14GB fp32)
- Nombre propuesto: "Ultra Dream Nexus"
- Modelo final en: `F:/Modelos/checkpoints/triultra_final_xtrio_50_35_15_fp32.safetensors`
