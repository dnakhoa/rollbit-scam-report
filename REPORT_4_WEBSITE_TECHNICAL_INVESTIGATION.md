# Report 4: Website Technical Investigation
## Rollbit / Bull Gaming N.V. — DNS, Edge Infrastructure, Public Web Stack, and License-Verification Friction
**Date:** April 19, 2026 | **Classification:** Technical Appendix
**Companion:** ← [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md) | → [Report 7: Technical Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)

---

## Executive Summary

The main Rollbit application and its public-content stack are materially different systems:

- **`rollbit.com`** is fronted by **Cloudflare** and actively enforces a browser challenge that blocks straightforward passive inspection.
- **`blog.rollbit.com`** is a separate, public **Ghost** deployment that resolves through **Fastly** and remains fully indexable.
- **`rollbot.rollbit.com`** resolves to the same Cloudflare edge IPs as the main site.
- Public **license verification is currently inconclusive** from direct web checks, because a previously indexed Rollbit/Bull Gaming certificate URL now returns **Not Found**, while current CGA policy says B2C sites should expose a domain-specific certificate path via `cert.cga.cw`.

This does not prove wrongdoing by itself. It shows that the public web footprint is layered and that independent verification of the operational domain requires a browser-aware, timestamped capture process.

---

## 1. Passive Methods Used

This appendix relies on passive or low-impact checks only:

- DNS-over-HTTPS queries to Cloudflare
- direct edge-header inspection with `curl --resolve`
- TLS certificate inspection with `openssl s_client`
- archived passive scan evidence from `urlscan.io`
- live HTML/header inspection of `blog.rollbit.com`
- official Curaçao Gaming Authority policy pages

Because this workstation had `rollbit.com` locally overridden to localhost, DNS was validated through **DoH**, not the system resolver.

Current capture artifact:

- [scripts/web_surface_capture.py](./scripts/web_surface_capture.py)
- [output/web_surface_capture.json](./output/web_surface_capture.json)
- latest local raw-capture directory: `output/captures/web/20260425T104619Z`

The raw capture directory is ignored by git for public release. Publish the JSON summary and hashes; keep raw bodies local or private.

---

## 1.1 April 25, 2026 Capture Snapshot

The new web capture utility preserved DoH DNS, TLS metadata, HTTP headers, response bodies, and body hashes for four surfaces.

| Target | DNS / Edge | HTTP Result | Body SHA-256 Prefix | Capture Note |
|--------|------------|-------------|---------------------|--------------|
| `rollbit.com` | Cloudflare `104.20.26.76`, `172.66.170.17` | **HTTP/2 403** | `4be5da3178ba0422` | Cloudflare challenge body captured |
| `blog.rollbit.com` | `rollbit.ghost.io` -> Fastly A records | **HTTP/2 200** | `234ca47b237f4ab9` | Public Ghost HTML captured |
| `rollbot.rollbit.com` | Cloudflare `104.20.26.76`, `172.66.170.17` | **HTTP/2 200** | `a18a6c7921ee03fa` | Static Rollbot/NFT-linking HTML captured |
| `cert.cga.cw/page/certification_policy` | Cloudflare `172.67.71.89`, `104.26.4.227`, `104.26.5.227` | **HTTP/2 200** | `8c138281c463af80` | CGA policy page captured |

TLS metadata from the same capture:

| Host | Certificate Subject | Issuer | Validity Window |
|------|---------------------|--------|-----------------|
| `rollbit.com` | `CN=rollbit.com` | Let's Encrypt E8 | Apr 9, 2026 to Jul 8, 2026 |
| `blog.rollbit.com` | `CN=blog.rollbit.com` | Certainly Intermediate R1 | Apr 19, 2026 to May 19, 2026 |
| `rollbot.rollbit.com` | `CN=rollbit.com` | Let's Encrypt E8 | Apr 9, 2026 to Jul 8, 2026 |
| `cert.cga.cw` | `CN=cga.cw` | Google Trust Services WE1 | Mar 3, 2026 to Jun 1, 2026 |

---

## 2. Main Domain Infrastructure: `rollbit.com`

### 2.1 DNS and nameserver layer

As of **April 19, 2026**, DNS-over-HTTPS returned:

| Record Type | Value |
|-------------|-------|
| A | `104.20.26.76` |
| A | `172.66.170.17` |
| NS | `penny.ns.cloudflare.com` |
| NS | `sullivan.ns.cloudflare.com` |

### 2.2 Edge behavior

A direct request to the live Cloudflare edge returned:

- **HTTP/2 403**
- `cf-mitigated: challenge`
- `server: cloudflare`
- `strict-transport-security: max-age=15552000; includeSubDomains; preload`
- `x-frame-options: SAMEORIGIN`
- `x-content-type-options: nosniff`
- strong `cross-origin-*` isolation headers

### 2.3 What the HTML actually shows

The returned document was not the application. It was Cloudflare's:

- **"Just a moment..."** interstitial
- with JavaScript challenge orchestration
- and explicit instruction to **enable JavaScript and cookies**

This means the transactional site is intentionally difficult to inspect through ordinary passive HTTP methods.

### 2.4 TLS certificate

The live certificate on the Rollbit edge presented:

| Field | Value |
|-------|-------|
| Subject | `CN=rollbit.com` |
| Issuer | `Let's Encrypt E8` |
| Not Before | `Apr 9 18:41:15 2026 GMT` |
| Not After | `Jul 8 18:41:14 2026 GMT` |

This is consistent with a modern, short-lived edge certificate rotation.

---

## 3. Archived Passive Scan Evidence

`urlscan.io` provides an older passive look at the site from **May 3, 2024**.

The scan showed:

- main IP on **Cloudflare**
- page title **"Nur einen Moment..."**
- only **11 HTTP transactions**
- **Cloudflare Browser Insights** present
- the primary request returning a challenge page rather than application content
- no visible outbound links captured from the main page because the challenge gate intercepted the session first

In other words, the challenge posture is not new; it has been observable for at least two years.

Source:

- `urlscan.io` result: https://urlscan.io/result/ae5a0a7d-6223-4610-b982-5c7258a2a285

---

## 4. Public Content Stack: `blog.rollbit.com`

The official blog is much easier to inspect than the gambling platform itself.

### 4.1 DNS path

DNS-over-HTTPS returned:

| Record Type | Value |
|-------------|-------|
| CNAME | `rollbit.ghost.io` |
| CNAME | `ghost.map.fastly.net` |
| A | `151.101.3.7` |
| A | `151.101.67.7` |
| A | `151.101.131.7` |
| A | `151.101.195.7` |

### 4.2 Response headers and software

The live blog returned:

- **HTTP/2 200**
- `server: openresty`
- `ghost-fastly: true;production`
- Fastly cache headers
- full public HTML

The page source exposed:

- `meta name="generator" content="Ghost 6.30"`
- Ghost membership portal scripts
- Ghost search scripts
- RSS feed
- public article metadata and author data

### 4.3 Operational significance

This split matters:

- the **main gambling / account platform** is shielded behind a Cloudflare challenge
- the **marketing / announcement layer** remains publicly indexable on Ghost/Fastly

That separation makes it easier for the operator to keep a polished public-facing communications channel online even when direct scrutiny of the transactional front end is limited.

---

## 5. Supporting Subdomain: `rollbot.rollbit.com`

`rollbot.rollbit.com` resolved to the same Cloudflare edge IPs as the main site:

- `104.20.26.76`
- `172.66.170.17`

This is consistent with Rollbit continuing to cluster its application and legacy/utility subdomains behind the same edge network, even while the blog is hosted separately.

---

## 6. Licensing Verification Friction

### 6.1 What official CGA policy says

The Curaçao Gaming Authority certification policy currently says:

- B2C operators must display a **Certificate of Operation Seal**
- clicking that seal must redirect to **`https://cert.cga.cw`**
- the certificate page must display:
  - the exact domain being accessed
  - the licensed operator
  - the current certificate status

### 6.2 What the direct check showed

A previously indexed Rollbit/Bull Gaming certificate URL, referenced in search results for:

- `rollbit.com`
- `Bull Gaming N.V.`
- `OGL/2024/1260/0494`

now redirects to a page that says:

- **"Not Found"**
- "The site you are looking for cannot be found in our registry, or has the wrong identification values."

### 6.3 What can and cannot be concluded

This **does not prove** that Rollbit is currently unlicensed.

It **does mean** that:

- direct public certificate verification for the operational domain was not cleanly reproducible on **April 19, 2026**
- the public evidence path is therefore weaker than ideal for a player-facing operator
- anyone relying on public domain-level licensing claims should preserve screenshots and timestamps when checking

Source pages:

- CGA certification policy: https://cert.cga.cw/page/certification_policy
- CGA online gaming regulation page: https://www.cga.cw/regulation/online-gaming

---

## 7. Current Operational Surface Still Looks Active

The web stack investigation also shows that Rollbit's communications layer is very much alive:

- the official blog homepage displayed posts dated **April 14, 2026**
- multiple promotions were published across **March and April 2026**
- the blog still links users directly back to `https://rollbit.com/`

This is a useful technical reminder:

- difficulty inspecting the main site should not be confused with inactivity
- the operator continues to maintain an active public marketing surface

---

## 8. Acquisition Checklist

[Report 7](./REPORT_7_TECHNICAL_DEEP_DIVE.md) treats the web layer as an acquisition problem. A defensible technical capture should preserve more than a screenshot.

Minimum bundle per capture:

| Artifact | Purpose |
|----------|---------|
| DoH JSON for A / AAAA / CNAME / NS | Resolver-independent DNS record preservation |
| TLS certificate details and fingerprint | Edge certificate attribution and rotation tracking |
| HTTP status, headers, and redirect chain | Challenge, cache, security-header, and routing evidence |
| Raw response body and body hash | Reproducible proof of challenge page or HTML content |
| Browser screenshot when rendering matters | Visual preservation of challenge or certificate state |
| urlscan / archive references | Independent passive corroboration when live access is blocked |

The main app, Rollbot subdomain, blog, and certificate-verification path should be captured as separate surfaces. They are not the same infrastructure problem.

---

## 9. Investigative Takeaways

1. **Main-site inspection is intentionally gated.** Anyone trying to archive Rollbit's live front end should expect Cloudflare challenge friction.
2. **The public content stack is easier to preserve than the product stack.** Blog content can be archived cleanly; the account-facing app cannot.
3. **The infrastructure is layered.** Cloudflare protects the main domain and Rollbot subdomain, while the blog runs on Ghost/Fastly.
4. **Public licensing validation remains inconclusive from direct web checks.** That is itself a meaningful due-diligence finding.

---

## Sources

- `urlscan.io` Rollbit scan: https://urlscan.io/result/ae5a0a7d-6223-4610-b982-5c7258a2a285
- Rollbit blog homepage: https://blog.rollbit.com/
- CGA certification policy: https://cert.cga.cw/page/certification_policy
- CGA online gaming page: https://www.cga.cw/regulation/online-gaming

---

*Continue to [Report 5: Public Event and Flow Timeline](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md) for the external media chronology.*
