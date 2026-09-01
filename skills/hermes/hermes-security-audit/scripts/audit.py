import os, json, re, subprocess, sys
from pathlib import Path

def load_yaml(path):
    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

def load_env(path):
    secrets = []
    pattern = re.compile(r'(?i)(?:API|TOKEN|KEY|SECRET)[_\-]?\w*\s*=?\s*.+')
    if not path.exists():
        return []
    for line in path.read_text(encoding='utf-8').splitlines():
        if pattern.search(line) and not line.strip().startswith('#'):
            secrets.append(line.strip())
    return secrets

def check_config():
    home = Path(os.getenv('HERMES_HOME') or os.path.expanduser('~/.hermes'))
    cfg_path = home / 'config.yaml'
    env_path = home / '.env'
    cfg = load_yaml(cfg_path) if cfg_path.exists() else None
    env_secrets = load_env(env_path)
    return cfg_path, cfg, env_path, env_secrets

def list_skills():
    home = Path(os.getenv('HERMES_HOME') or os.path.expanduser('~/.hermes'))
    skills_dir = home / 'skills'
    risky = []
    for sk in skills_dir.rglob('SKILL.md'):
        try:
            text = sk.read_text(encoding='utf-8')
        except Exception:
            continue
        if re.search(r'(?i)rm\s+-rf|sudo|chmod\s+777|kill\s+-9', text):
            risky.append(str(sk))
    return risky

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return '', str(e)

def check_mcp():
    out, err = run_cmd('hermes mcp list')
    unavailable = []
    for line in out.splitlines():
        if 'error' in line.lower() or 'unavailable' in line.lower():
            unavailable.append(line.strip())
    return out, unavailable

def check_cron():
    out, err = run_cmd('hermes cron list')
    missing = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) > 2:
            script = parts[-1]
            if not Path(script).exists():
                missing.append(script)
    return out, missing

def main():
    report = []
    cfg_path, cfg, env_path, env_secrets = check_config()
    report.append('## Configuración')
    report.append(f'* Config file: {cfg_path}')
    report.append(f'* .env file: {env_path}')
    if env_secrets:
        report.append('### Secretos potenciales en .env')
        for s in env_secrets:
            report.append(f'- `{s}`')
    else:
        report.append('No se detectaron posibles secretos en `.env`.')
    risky_skills = list_skills()
    report.append('\n## Skills con comandos de alto riesgo')
    if risky_skills:
        for p in risky_skills:
            report.append(f'- {p}')
    else:
        report.append('No se encontraron skills con comandos de alto riesgo.')
    mcp_out, mcp_issues = check_mcp()
    report.append('\n## MCP')
    report.append('```')
    report.append(mcp_out)
    report.append('```')
    if mcp_issues:
        report.append('### Problemas detectados')
        for i in mcp_issues:
            report.append(f'- {i}')
    else:
        report.append('Todos los servidores MCP parecen activos.')
    cron_out, cron_missing = check_cron()
    report.append('\n## Cron')
    report.append('```')
    report.append(cron_out)
    report.append('```')
    if cron_missing:
        report.append('### Scripts de cron no encontrados')
        for s in cron_missing:
            report.append(f'- {s}')
    else:
        report.append('Todos los scripts de cron existen.')
    exit_code = 0
    if env_secrets or risky_skills or mcp_issues or cron_missing:
        if env_secrets or cron_missing:
            exit_code = 2
        else:
            exit_code = 1
    markdown = '\n'.join(report)
    print(markdown)
    summary = {
        'secrets': bool(env_secrets),
        'risky_skills': bool(risky_skills),
        'mcp_issues': bool(mcp_issues),
        'cron_missing': bool(cron_missing),
        'exit_code': exit_code,
    }
    sys.stderr.write(json.dumps(summary))

if __name__ == '__main__':
    main()
