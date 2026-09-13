#!/usr/bin/env python
import os
import subprocess
import sys
import time

def run_hermes_chat(model, prompt="test"):
    """Run hermes chat -q with given model, return (success, output)."""
    cmd = ["hermes", "chat", "--oneshot", "-q", prompt, "-m", model, "--timeout", "10"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            # Filter out banner lines; look for actual response after the first empty line?
            # Simple: if stdout non-empty and not just the usage/help, consider success.
            out = result.stdout.strip()
            if out and not out.startswith("usage:") and not out.startswith("Welcome to Hermes Agent"):
                return True, out
            else:
                # maybe the response is in stderr? unlikely
                return False, "no meaningful output"
        else:
            return False, result.stderr.strip() or result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)

def set_default_model(model):
    subprocess.run(["hermes", "config", "set", "model.default", model], check=False)
    subprocess.run(["hermes", "config", "set", "model.provider", ""], check=False)  # let alias decide

def reload_config():
    subprocess.run(["hermes", "config", "check"], check=False)
    # In a running session, /reload would be needed; we just advise user.

def main():
    free_models = [
        "deepseek-v4.1-flash",
        "deepseek-v4-flash",
        "mimo-v2.5",
        "hy3-free",
        "orcarouter",
        "aihubmix-glm",
        "bai-glm",
        "experiential",
        "bai-hy3",
        "bai-mimo",
    ]
    paid_model = "glm-5.3"
    
    print("🔍 Starting model fallback optimizer...")
    for model in free_models:
        print(f"🔍 Testing free model: {model}")
        success, output = run_hermes_chat(model)
        if success:
            print(f"✅ Success! Setting model.default to {model}")
            set_default_model(model)
            print("💡 Run 'hermes config check' and restart chat to apply.")
            return
        else:
            print(f"❌ Failed: {output[:80]}")
    
    print("💰 All free models exhausted. Falling back to paid GLM 5.3.")
    set_default_model(paid_model)
    print("💡 Run 'hermes config check' and restart chat to apply.")

if __name__ == "__main__":
    main()
