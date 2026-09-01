# ChatGPT session cookies needed for the /backend-api/f/conversation image route
#
# The openai-codex Bearer token (auth.json) is NOT enough. Export these from the
# user's Chrome on https://chatgpt.com via Cookie-Editor extension (Export -> JSON)
# or DevTools -> Application -> Cookies. Save as cookies.json, then run:
#   python scripts/probe_chatgpt_image.py --with-cookies cookies.json

REQUIRED_COOKIE_NAMES = [
    "__Secure-next-auth.session-token.0",   # encrypted session JWT (primary)
    "__Secure-next-auth.session-token.1",   # secondary fragment
    "cf_clearance",                          # Cloudflare bot clearance
    "_puid",                                # user id (e.g. user-lFl3bfJ762KlGf4SLPBr8BCI)
    "oai-did",                              # device id (uuid)
]

# Optional but present in the live request: oai-sc, oai-gn, _cfuvid, __cf_bm, _uasid, _umsid
# The Cookie-Editor JSON export format this skill expects:
#   [{"name": "...", "value": "...", "domain": "chatgpt.com", ...}, ...]

WARNING: cookies are session-equivalent secrets. Use only locally, delete after the task,
never commit to git, never paste raw values into chat logs or notes.
