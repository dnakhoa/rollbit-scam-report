#!/usr/bin/env python3
"""
Capture Rollbit-related public web surfaces for forensic preservation.

The script uses low-impact requests:
    - Cloudflare DNS-over-HTTPS for resolver-independent DNS records
    - openssl for TLS certificate metadata
    - curl with --resolve for HTTP headers/body capture when an A record exists

Outputs:
    output/web_surface_capture.json
    output/captures/web/<timestamp>/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
CAPTURE_ROOT = OUTPUT_DIR / "captures" / "web"
SUMMARY_JSON = OUTPUT_DIR / "web_surface_capture.json"


TARGETS = [
    {"name": "main_app", "host": "rollbit.com", "path": "/"},
    {"name": "blog", "host": "blog.rollbit.com", "path": "/"},
    {"name": "rollbot", "host": "rollbot.rollbit.com", "path": "/"},
    {"name": "cga_policy", "host": "cert.cga.cw", "path": "/page/certification_policy"},
]


DNS_TYPES = ["A", "AAAA", "CNAME", "NS", "TXT"]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_command(args: list[str], timeout: int = 45) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "args": args,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except FileNotFoundError as exc:
        return {"args": args, "returncode": None, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "args": args,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": f"timeout after {timeout}s",
        }


def doh_query(host: str, record_type: str) -> dict[str, Any]:
    if not HAS_REQUESTS:
        return {"error": "requests not installed"}
    try:
        resp = requests.get(
            "https://cloudflare-dns.com/dns-query",
            params={"name": host, "type": record_type},
            headers={"accept": "application/dns-json"},
            timeout=20,
        )
        return {
            "status_code": resp.status_code,
            "json": resp.json(),
        }
    except Exception as exc:
        return {"error": str(exc)}


def first_a_record(dns_records: dict[str, Any]) -> str:
    answers = dns_records.get("A", {}).get("json", {}).get("Answer", []) or []
    for answer in answers:
        data = answer.get("data", "")
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", data):
            return data
    return ""


def capture_tls(host: str, ip: str) -> dict[str, Any]:
    if not ip:
        return {"error": "no A record available"}
    cmd = [
        "openssl", "s_client",
        "-servername", host,
        "-connect", f"{ip}:443",
        "-showcerts",
    ]
    raw = run_command(cmd, timeout=30)
    cert_input = raw.get("stdout", "")
    if not cert_input:
        return {"raw": raw, "parsed": {}}

    parse_proc = subprocess.run(
        [
            "openssl", "x509",
            "-noout",
            "-subject",
            "-issuer",
            "-dates",
            "-fingerprint",
            "-sha256",
            "-ext",
            "subjectAltName",
        ],
        input=cert_input,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    return {
        "connect_ip": ip,
        "raw_returncode": raw.get("returncode"),
        "raw_stderr": raw.get("stderr", "")[-2000:],
        "parsed_returncode": parse_proc.returncode,
        "parsed": parse_proc.stdout,
        "parsed_stderr": parse_proc.stderr[-2000:],
    }


def capture_http(target: dict[str, str], ip: str, capture_dir: Path) -> dict[str, Any]:
    host = target["host"]
    path = target.get("path", "/")
    if not path.startswith("/"):
        path = "/" + path
    url = f"https://{host}{path}"
    base = safe_name(f"{target['name']}_{host}")
    headers_path = capture_dir / f"{base}.headers.txt"
    body_path = capture_dir / f"{base}.body.bin"

    cmd = [
        "curl",
        "-sS",
        "-L",
        "--compressed",
        "--max-time",
        "45",
        "-D",
        str(headers_path),
        "-o",
        str(body_path),
    ]
    if ip:
        cmd.extend(["--resolve", f"{host}:443:{ip}"])
    cmd.append(url)

    result = run_command(cmd, timeout=60)
    headers_text = headers_path.read_text(errors="replace") if headers_path.exists() else ""
    status_lines = [line.strip() for line in headers_text.splitlines() if line.startswith("HTTP/")]

    body_hash = sha256_file(body_path) if body_path.exists() else ""
    body_size = body_path.stat().st_size if body_path.exists() else 0

    return {
        "url": url,
        "connect_ip": ip,
        "command": cmd,
        "returncode": result.get("returncode"),
        "stderr": result.get("stderr", "")[-2000:],
        "headers_file": str(headers_path.relative_to(ROOT)) if headers_path.exists() else "",
        "body_file": str(body_path.relative_to(ROOT)) if body_path.exists() else "",
        "body_sha256": body_hash,
        "body_size_bytes": body_size,
        "status_lines": status_lines,
        "final_status": status_lines[-1] if status_lines else "",
    }


def capture_target(target: dict[str, str], capture_dir: Path) -> dict[str, Any]:
    host = target["host"]
    dns_records = {record_type: doh_query(host, record_type) for record_type in DNS_TYPES}
    ip = first_a_record(dns_records)
    tls = capture_tls(host, ip)
    http = capture_http(target, ip, capture_dir)

    return {
        "target": target,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "dns": dns_records,
        "selected_ip": ip,
        "tls": tls,
        "http": http,
    }


def run(targets: list[dict[str, str]] = TARGETS) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    capture_dir = CAPTURE_ROOT / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)

    results = [capture_target(target, capture_dir) for target in targets]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capture_dir": str(capture_dir.relative_to(ROOT)),
        "method": "DoH DNS + openssl TLS + curl HTTP capture",
        "results": results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_JSON.open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture Rollbit web-surface artifacts")
    parser.add_argument("--host", action="append", help="Override targets with host names")
    args = parser.parse_args()

    targets = TARGETS
    if args.host:
        targets = [{"name": safe_name(host), "host": host, "path": "/"} for host in args.host]

    payload = run(targets)
    print("Web surface capture complete")
    print(f"  Targets: {len(payload['results'])}")
    print(f"  Capture dir: {payload['capture_dir']}")
    print(f"  Summary: {SUMMARY_JSON}")
    for result in payload["results"]:
        target = result["target"]
        http = result["http"]
        print(f"  - {target['host']}: {http.get('final_status') or 'no status'}; body sha256={http.get('body_sha256', '')[:16]}")


if __name__ == "__main__":
    main()
