#!/usr/bin/env python
# hermes-verify template: assert a skill change works on a GENUINE valid input.
# Copy to %TEMP%/hermes-verify-<topic>.py, adapt, run, then DELETE it.
import os, subprocess, sys, io
from PIL import Image

SKILL = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'skills',
                     '<SKILL_DIR>', '<script>.py')
TMP = 'C:/Users/GIOWIC~1/AppData/Local/Temp'
os.chdir(TMP)

def openable(p):
    try:
        im = Image.open(p); im.load(); return True, im.size
    except Exception as e:
        return False, str(e)[:60]

# 1. GENUINE valid input (no hand-injected malformed segments)
im = Image.new('RGB', (48, 48), (40, 120, 200))
im.save('in.jpg', quality=90)
ok_in, _ = openable('in.jpg')

# 2. Run the (patched) skill
r = subprocess.run([sys.executable, SKILL, 'in.jpg', '-o', 'out.jpg'],
                   capture_output=True, text=True)

# 3. Output must be valid/openable AND behavior changed as intended
ok_out, info = openable('out.jpg')
magic = open('out.jpg','rb').read()
magic_ok = magic[:2] == b'\xff\xd8' and magic[-2:] == b'\xff\xd9'
print("in_ok=%s rc0=%s out_ok=%s magic_ok=%s" % (ok_in, r.returncode==0, ok_out, magic_ok))

for f in ('in.jpg','out.jpg'):
    try: os.remove(f)
    except OSError: pass

print("VERIFIED_OK" if (ok_in and r.returncode==0 and ok_out and magic_ok) else "VERIFIED_FAIL")
