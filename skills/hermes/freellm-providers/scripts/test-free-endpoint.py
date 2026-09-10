#!/usr/bin/env python3
"""
test-free-endpoint.py — Test any free LLM endpoint from freellm.net providers.

Usage:
    python test-free-endpoint.py --provider groq --api-key gsk_xxx --model moonshotai/kimi-k2-instruct
    python test-free-endpoint.py --base-url https://api.groq.com/openai/v1 --api-key gsk_xxx --model moonshotai/kimi-k2-instruct
    python test-free-endpoint.py --hermes-test --provider groq  # Uses Hermes env vars

Exits 0 on success, 1 on failure.
"""
import argparse, os, sys, json, urllib.request, time

# Known provider endpoints (base_url, model, env_var)
PROVIDERS = {
    "groq":       {"base_url": "https://api.groq.com/openai/v1",        "model": "moonshotai/kimi-k2-instruct",      "env": "GROQ_API_KEY"},
    "gemini":     {"base_url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-3.6-flash",  "env": "GEMINI_API_KEY"},
    "github":     {"base_url": "https://models.github.ai/inference",    "model": "Phi-4",                              "env": "GITHUB_TOKEN"},
    "mistral":    {"base_url": "https://api.mistral.ai/v1",             "model": "mistral-medium-3-5-128b",           "env": "MISTRAL_API_KEY"},
    "cohere":     {"base_url": "https://api.cohere.com/v2",             "model": "command-a-218b",                    "env": "COHERE_API_KEY"},
    "deepseek":   {"base_url": "https://api.deepseek.com/v1",           "model": "deepseek-chat-v3-2",                "env": "DEEPSEEK_API_KEY"},
    "cerebras":   {"base_url": "https://api.cerebras.ai/v1",            "model": "llama3.1-70b",                      "env": "CEREBRAS_API_KEY"},
    "xai":        {"base_url": "https://api.x.ai/v1",                   "model": "grok-4-3",                           "env": "XAI_API_KEY"},
    "huggingface":{"base_url": "https://router.huggingface.co/v1",      "model": "meta-llama-3-1-8b-instruct",        "env": "HF_TOKEN"},
    "llm7":       {"base_url": "https://api.llm7.io/v1",                "model": "deepseek-v3",                        "env": "LLM7_API_KEY"},
    "ai21":       {"base_url": "https://studio.ai21.com/studio/v1",    "model": "jamba-large-1-7",                    "env": "AI21_API_KEY"},
    "zhipu":      {"base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4.7",                            "env": "ZHIPU_API_KEY"},
    "sambanova":  {"base_url": "https://api.sambanova.ai/v1",           "model": "deepseek-v3-2-preview",             "env": "SAMBANOVA_API_KEY"},
    "nvidia":     {"base_url": "https://integrate.api.nvidia.com/v1",   "model": "z-ai/glm-5.2",                      "env": "NVAPI_KEY"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1",          "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "env": "OPENROUTER_API_KEY"},
}

def test_endpoint(base_url, api_key, model, timeout=30):
    """Make a single test call to any OpenAI-compatible endpoint."""
    # Normalize base_url
    base_url = base_url.rstrip("/")
    url = f"{base_url}/chat/completions"
    
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say hello in exactly 5 words."}],
        "max_tokens": 20,
        "temperature": 0
    }).encode("utf-8")
    
    # Build headers — Gemini uses X-Goog-Api-Key, others use Bearer
    headers = {"Content-Type": "application/json"}
    if "generativelanguage.googleapis.com" in base_url:
        headers["X-Goog-Api-Key"] = api_key
        # Gemini endpoint is different
        url = f"{base_url}/models/{model}:generateContent"
        body = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": "Say hello in exactly 5 words."}]}],
            "generationConfig": {"maxOutputTokens": 20}
        }).encode("utf-8")
    elif "cloudflare.com" in base_url:
        headers["Authorization"] = f"Bearer {api_key}"
        # Cloudflare uses account_id in URL
        print("⚠️ Cloudflare requires account_id in URL. Use direct --base-url with full path.")
    elif "open.bigmodel.cn" in base_url:
        headers["Authorization"] = f"Bearer {api_key}"
    elif "bigmodel.cn" in base_url:
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["Authorization"] = f"Bearer {api_key}"
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                latency = time.time() - t0
                data = json.loads(resp.read().decode("utf-8"))
            
            # Parse response based on provider
            if "generativelanguage.googleapis.com" in base_url:
                if "candidates" in data and data["candidates"]:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    text = json.dumps(data, indent=2)[:200]
            elif "choices" in data:
                text = data["choices"][0]["message"]["content"]
            else:
                text = json.dumps(data, indent=2)[:200]
            
            print(f"✅ {model} — OK ({latency:.1f}s)")
            print(f"   Response: {text}")
            return True
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:500]
            print(f"⚠️  Attempt {attempt+1}: HTTP {e.code} — {err}")
            if e.code in (401, 403):
                print("❌ Auth error — check your API key")
                return False
            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Attempt {attempt+1}: {type(e).__name__}: {str(e)[:200]}")
            time.sleep(2)
    
    print(f"❌ {model} — Failed after 3 attempts")
    return False

def main():
    parser = argparse.ArgumentParser(description="Test any free LLM endpoint")
    parser.add_argument("--provider", help="Provider name (groq, gemini, nvidia, etc.)")
    parser.add_argument("--base-url", help="Base URL (overrides provider lookup)")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--hermes-test", action="store_true", help="Test using Hermes env vars")
    args = parser.parse_args()
    
    base_url = args.base_url
    api_key = args.api_key
    model = args.model
    
    # Load from provider alias
    if args.provider and args.provider.lower() in PROVIDERS:
        p = PROVIDERS[args.provider.lower()]
        base_url = base_url or p["base_url"]
        model = model or p["model"]
        api_key = api_key or os.environ.get(p["env"])
    
    # Hermes test mode: try to use hermes config
    if args.hermes_test:
        if args.provider and args.provider.lower() in PROVIDERS:
            p = PROVIDERS[args.provider.lower()]
            api_key = os.environ.get(p["env"])
            if not api_key:
                # Try reading from .env
                env_path = os.path.expanduser("~/.env")
                if os.path.exists(env_path):
                    with open(env_path) as f:
                        for line in f:
                            if line.startswith(f"{p['env']}="):
                                api_key = line.strip().split("=", 1)[1]
                                break
            if not api_key:
                print(f"❌ No {p['env']} found in env or ~/.env")
                sys.exit(1)
        else:
            print("❌ --hermes-test requires --provider")
            sys.exit(1)
    
    if not base_url or not api_key or not model:
        parser.print_help()
        print("\n❌ Missing required args. Use --provider or specify all three: --base-url --api-key --model")
        sys.exit(1)
    
    print(f"🔧 Testing: {model}")
    print(f"   Endpoint: {base_url}/chat/completions")
    print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    success = test_endpoint(base_url, api_key, model)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()