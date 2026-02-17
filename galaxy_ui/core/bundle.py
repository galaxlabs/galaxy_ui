"""
Bundle helpers: compute hash/version and assemble payload for the runtime loader.
"""
from __future__ import annotations
import hashlib


def bundle_hash(*parts: str) -> str:
    raw = "\n".join([p or "" for p in parts]).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]
