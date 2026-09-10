#!/usr/bin/env python3
"""
write-fallbacks.py — Escribe fallback_providers en config.yaml de Hermes
Usa este script porque `hermes config set` NO soporta listas/arrays.

Usage:
    python write-fallbacks.py --provider groq  # escribe fallback para Groq
    python write-fallbacks.py --all-free         # escribe cadena completa sin CC
    python write-fallbacks.py --list              # lista proveedores disponibles
"""
import argparse, os, sys, json, yaml, shutil, re

CONFIG_PATH = os.path.join(os.environ.get("APPDATA", ""), "hermes", "config.yaml")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.expanduser("~/.config/hermes/config.yaml")
    if not os.path.exists(CONFIG_PATH):
        CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml")

PROVIDERS = {
    "groq":       {"model": "moonshotai/kimi-k2-instruct",      "base_url": "https://api.groq.com/openai/v1",                     "env": "GROQ_API_KEY"},
    "gemini":     {"model": "gemini-3.6-flash",                 "base_url": "https://generativelanguage.googleapis.com/v1beta",  "env": "GEMINI_API_KEY"},
    "mistral":    {"model": "mistral-medium-3-5-128b",          "base_url": "https://api.mistral.ai/v1",                          "env": "MISTRAL_API_KEY"},
    "cohere":     {"model": "command-a-218b",                   "base_url": "https://api.cohere.com/v2",                          "env": "COHERE_API_KEY"},
    "deepseek":   {"model": "deepseek-chat-v3-2",               "base_url": "https://api.deepseek.com/v1",                        "env": "DEEPSEEK_API_KEY"},
    "cerebras":   {"model": "llama3.1-70b",                     "base_url": "https://api.cerebras.ai/v1",                         "env": "CEREBRAS_API_KEY"},
    "nvidia":     {"model": "z-ai/glm-5.2",                     "base_url": "https://integrate.api.nvidia.com/v1",                "env": "NVAPI_KEY"},
    "openrouter": {"model": "nvidia/nemotron-3-ultra-550b-a55b:free", "base_url": "https://openrouter.ai/api/v1",                "env": "OPENROUTER_API_KEY"},
    "xai":        {"model": "grok-4-3",                          "base_url": "https://api.x.ai/v1",                                "env": "XAI_API_KEY"},
    "ai21":       {"model": "jamba-large-1-7",                  "base_url": "https://studio.ai21.com/studio/v1",                  "env": "AI21_API_KEY"},
    "huggingface":{"model": "meta-llama-3-1-8b-instruct",       "base_url": "https://router.huggingface.co/v1",                   "env": "HF_TOKEN"},
    "llm7":       {"model": "deepseek-v3",                      "base_url": "https://api.llm7.io/v1",                              "env": "LLM7_API_KEY"},
    "sambanova":  {"model": "deepseek-v3-2-preview",            "base_url": "https://api.sambanova.ai/v1",                        "env": "SAMBANOVA_API_KEY"},
    "zhipu":      {"model": "glm-4.7",                          "base_url": "https://open.bigmodel.cn/api/paas/v4",               "env": "ZHIPU_API_KEY"},
}

def get_key_from_env(env_var):
    """Try to get API key from environment or .env file."""
    key = os.environ.get(env_var)
    if key:
        return key
    
    # Try .env in APPDATA/hermes/
    for env_path in [
        os.path.join(os.environ.get("APPDATA", ""), "hermes", ".env"),
        os.path.expanduser("~/.env"),
        os.path.expanduser("~/.config/hermes/.env"),
    ]:
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{env_var}="):
                        return line.split("=", 1)[1]
    return None

def make_fallback_entry(provider_key):
    """Build a fallback_providers entry dict."""
    p = PROVIDERS[provider_key]
    api_key = get_key_from_env(p["env"])
    return {
        "provider": "custom",
        "model": p["model"],
        "base_url": p["base_url"],
        "api_key": api_key or f"<SET {p['env']}_HERE>",
        "api_mode": "openai"
    }

def main():
    parser = argparse.ArgumentParser(description="Write fallback providers to Hermes config.yaml")
    parser.add_argument("--provider", help="Provider key (groq, gemini, nvidia, etc.)")
    parser.add_argument("--all-free", action="store_true", help="Write full chain of no-CC providers")
    parser.add_argument("--list", action="store_true", help="List available providers")
    args = parser.parse_args()
    
    if args.list:
        print("Available providers for fallback:")
        for k, v in sorted(PROVIDERS.items()):
            print(f"  {k:15s} → {v['model']:40s} ({v['base_url']})")
        print("\nUsage: python write-fallbacks.py --provider <name>")
        print("       python write-fallbacks.py --all-free")
        return
    
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Config not found at {CONFIG_PATH}")
        sys.exit(1)
    
    # Read config
    with open(CONFIG_PATH, encoding="utf-8") as f:
        text = f.read()
    d = yaml.safe_load(text) or {}
    
    if args.provider:
        if args.provider not in PROVIDERS:
            print(f"❌ Unknown provider: {args.provider}")
            print(f"   Available: {', '.join(sorted(PROVIDERS.keys()))}")
            sys.exit(1)
        fallbacks = [make_fallback_entry(args.provider)]
    elif args.all_free:
        # Chain: no-CC providers first, then providers with verification
        no_cc = ["groq", "gemini", "mistral", "cohere", "deepseek", "cerebras", "xai", "ai21", "llm7", "huggingface"]
        with_verif = ["nvidia", "sambanova", "zhipu"]
        fallbacks = [make_fallback_entry(k) for k in no_cc]
        fallbacks += [make_fallback_entry(k) for k in with_verif]
    else:
        parser.print_help()
        return
    
    # Backup
    bak = CONFIG_PATH + f".bak.{int(__import__('time').time())}"
    shutil.copy2(CONFIG_PATH, bak)
    
    d["fallback_providers"] = fallbacks
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(d, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Written {len(fallbacks)} fallback(s) to {CONFIG_PATH}")
    print(f"   Backup: {bak}")
    for fb in fallbacks:
        key_preview = fb["api_key"][:8] + "..." if fb["api_key"] and fb["api_key"] != f"<SET _HERE>" else "❌ KEY MISSING"
        print(f"   • {fb['model']:45s} {key_preview}")

if __name__ == "__main__":
    main()