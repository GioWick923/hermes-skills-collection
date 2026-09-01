import os, sys, json, subprocess, urllib.request
from pathlib import Path

# Configurable defaults
DEFAULT_PORT = int(os.getenv('NEKO_PORT', '8080'))
CONTAINER_NAME = os.getenv('NEKO_CONTAINER', 'neko-master')
IMAGE = os.getenv('NEKO_IMAGE', 'foru17/neko-master')
HEALTH_ENDPOINT = f'http://localhost:{DEFAULT_PORT}/health'

def docker_cmd(cmd):
    result = subprocess.run(f'docker {cmd}', shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def ensure_image():
    # Pull if missing
    out, err, rc = docker_cmd('images -q ' + IMAGE)
    if not out:
        docker_cmd(f'pull {IMAGE}')

def container_running():
    out, err, rc = docker_cmd(f'inspect -f "{{{{.State.Running}}}}" {CONTAINER_NAME}')
    return out == 'true'

def start_container():
    out, err, rc = docker_cmd(f'start {CONTAINER_NAME}')
    return rc == 0

def health_check():
    try:
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=5) as resp:
            data = resp.read().decode()
            return True, data
    except Exception as e:
        return False, str(e)

def main():
    restart = '--restart' in sys.argv
    ensure_image()
    if not container_running():
        started = start_container()
        if not started:
            print('❌ No se pudo iniciar el contenedor.')
            sys.stderr.write(json.dumps({'healthy': False, 'error': 'container_start_failed'}))
            sys.exit(2)
    healthy, info = health_check()
    if healthy:
        print('✅ Contenedor está saludable.')
        print('Detalles:', info)
        sys.stderr.write(json.dumps({'healthy': True, 'info': info}))
        sys.exit(0)
    else:
        print('⚠️ Salud del contenedor fallida:', info)
        if restart:
            print('🔁 Intentando reiniciar el contenedor...')
            if start_container():
                # Re‑check after restart
                healthy2, info2 = health_check()
                if healthy2:
                    print('✅ Reinicio exitoso, contenedor saludable.')
                    sys.stderr.write(json.dumps({'healthy': True, 'info': info2}))
                    sys.exit(0)
        sys.stderr.write(json.dumps({'healthy': False, 'error': info}))
        sys.exit(1)

if __name__ == '__main__':
    main()
