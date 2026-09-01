#!/usr/bin/env python3
"""Ad-hoc verifier for the decompress() makedirs fix in
backend/huggingface/__init__.py (forge-neo mini fork).

Reproduces the exact FileNotFoundError bug: decompressing a bundled
*.tokenizer.json.xz into a per-model dir (e.g. Wan-AI/Wan2.1-T2V-14B/tokenizer/)
whose parent folders don't exist after pruning.

PASS = the patched decompress() creates the destination tree and writes the file.

Usage:
    python verify_decompress_makedirs.py "C:/path/to/mini-forge-neo/backend/huggingface/__init__.py"
If no arg given, tries the default Windows user path.
"""
import sys, os, tempfile, importlib.util, lzma, shutil, py_compile


def main() -> int:
    hf_init = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        r"~\mini-forge-neo\backend\huggingface\__init__.py")
    if not os.path.isfile(hf_init):
        print(f"FAIL: not found: {hf_init}")
        return 2

    try:
        py_compile.compile(hf_init, doraise=True)
        compile_ok = True
    except Exception as e:
        compile_ok = False
        print("compile error:", e)

    spec = importlib.util.spec_from_file_location("hf_patched", hf_init)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    tmp = tempfile.mkdtemp(prefix="hermes-verify-")
    try:
        src = os.path.join(tmp, "s.json.xz")
        payload = b'{"ok":true}'
        with lzma.open(src, "wb") as f:
            f.write(payload)
        dst = os.path.join(tmp, "Wan-AI", "Wan2.1-T2V-14B", "tokenizer", "tokenizer.json")
        before = os.path.isdir(os.path.dirname(dst))
        mod.decompress(src, dst)
        after = os.path.isdir(os.path.dirname(dst))
        with open(dst, "rb") as f:
            content_ok = f.read() == payload
        passed = compile_ok and (not before) and after and content_ok
        print(f"py_compile OK: {compile_ok}")
        print(f"dir before/after: {before} -> {after}")
        print(f"content correct: {content_ok}")
        print("VERDICT:", "PASS" if passed else "FAIL")
        return 0 if passed else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
