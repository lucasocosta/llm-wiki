"""Verify code provenance against Git without changing the checkout."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


def git_output(root: Path, *args: str) -> bytes | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def code_file_version(path: Path) -> dict:
    """A commit is attributed only when it contains the bytes actually read."""
    if not path.is_file():
        return {"unverifiable": "source file no longer exists"}
    content = path.read_bytes()
    version = {"content_hash": hashlib.sha256(content).hexdigest()}
    root_bytes = git_output(path.parent, "rev-parse", "--show-toplevel")
    if root_bytes:
        root = Path(root_bytes.decode().strip())
        relative = path.resolve().relative_to(root.resolve()).as_posix()
        committed = git_output(root, "show", f"HEAD:{relative}")
        sha = git_output(root, "log", "-1", "--format=%H", "--", relative)
        if committed == content and sha and sha.strip():
            version["commit"] = sha.decode().strip()
            return version
    version["unverifiable"] = "content has no matching committed revision (untracked, modified, or outside Git)"
    return version


def validate_code_pin(base: Path, commit: str | None, files: list[Path]) -> None:
    """External Sources must be clean at the requested commit before delivery."""
    if not commit or not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
        raise ValueError(f"external Source requires a commit SHA, got {commit!r}")
    resolved = git_output(base, "rev-parse", "--verify", f"{commit}^{{commit}}")
    head = git_output(base, "rev-parse", "--verify", "HEAD")
    if not resolved or not head or resolved.strip() != head.strip():
        raise ValueError(f"checkout does not match declared commit {commit}; check out that revision explicitly")
    for path in files:
        version = code_file_version(path)
        if "unverifiable" in version:
            raise ValueError(f"{path}: content does not match declared commit {commit}; {version['unverifiable']}")
