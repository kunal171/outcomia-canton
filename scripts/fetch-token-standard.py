#!/usr/bin/env python3
"""Fetch pinned interface DARs; never rebuild them with a different SDK."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 4 * 1024 * 1024


def fetch_artifact(url, destination, expected_sha256, opener=urlopen):
    """Keep verified caches offline; reject bad downloads before replacing files."""
    if destination.is_file() and destination.stat().st_size <= MAX_BYTES and hashlib.sha256(destination.read_bytes()).hexdigest() == expected_sha256:
        return
    with opener(url, timeout=30) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or not data.startswith(b"PK"):
        raise ValueError(f"Invalid or oversized DAR: {destination.name}")
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError(f"Checksum mismatch: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def locked_urls(lock):
    """Require pinned official files; the manifest cannot select another host/path."""
    if lock["repository"] != "canton-network/splice" or lock["directory"] != "daml/dars":
        raise ValueError("Unexpected token-standard source")
    if not re.fullmatch(r"[0-9a-f]{40}", lock["revision"]):
        raise ValueError("Token-standard source must use a full commit hash")
    entries = []
    names = set()
    for artifact in lock["artifacts"]:
        name, digest = artifact["name"], artifact["sha256"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.dar", name) or name in names:
            raise ValueError("Invalid or duplicate DAR filename")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid DAR checksum")
        names.add(name)
        url = f"https://raw.githubusercontent.com/canton-network/splice/{lock['revision']}/daml/dars/{name}"
        entries.append((url, name, digest))
    return entries


def main():
    lock = json.loads((ROOT / "contracts/deps/token-standard.lock.json").read_text())
    for url, name, digest in locked_urls(lock):
        fetch_artifact(url, ROOT / "target/deps" / name, digest)
    print("Token Standard DAR checksums verified.")


if __name__ == "__main__":
    main()
