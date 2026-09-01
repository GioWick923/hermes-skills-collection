# OSINT Legal Map (quick reference)

Rule of thumb: **Passive + public + no deception = legal.** Active + unauthorized + deception = illegal.

## Legal / allowed (passive OSINT)
- WHOIS, DNS, SSL/certificate inspection (e.g. `domain-intel`)
- Web search (DuckDuckGo, SearXNG), reading public web pages
- Public social-media profiles, public satellite imagery (Google Earth)
- Defensive security: auditing YOUR OWN domain/server, CTFs, authorized labs
- Explaining how an attack works for defense (without executing it)

## Illegal / disallowed (regardless of a "warning")
- Hacking / unauthorized intrusion into systems
- Scraping that violates ToS + bypassing CAPTCHA/anti-bot protections
- Social engineering to deceive someone into revealing data
- Using breached / stolen databases
- Doxxing: publishing personal data to harm someone
- Intercepting traffic on networks you don't own
- Aggressive port/server enumeration (active scanning)
- OSINT to stalk / harass / target a person

## Gray zone (depends on jurisdiction/context)
- OSINT on minors (almost always illegal)
- Gathering a competitor's employee data to spy (labor/competition law)
- Cross-referencing public data into profiles without consent (GDPR / privacy law)

## Note
Tools like `domain-intel` are passive + public → always on the legal side.
The 4 hard "never" rules (break systems, doxxing, data w/o consent, aggressive bypass)
are system candados, not user-configured, and a disclaimer does not override them.
