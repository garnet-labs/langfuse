"""Trusted-base CODEOWNERS context for the approval engine."""

import re
from pathlib import Path


def _pattern(pattern: str) -> re.Pattern:
    if any(char in pattern for char in "![]\\"):
        raise ValueError(f"unsupported CODEOWNERS pattern: {pattern}")
    anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
    pattern = pattern.lstrip("/").rstrip("/")
    if not pattern:
        pattern = "**"
    parts = []
    index = 0
    while index < len(pattern):
        if pattern[index:index + 3] == "**/":
            parts.append("(?:.*/)?")
            index += 3
        elif pattern[index:index + 2] == "**":
            parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(pattern[index]))
            index += 1
    return re.compile(("^" if anchored else "(?:^|/)") + "".join(parts) + "(?:/.*)?$")


class CodeownersResolver:
    """Last matching rule wins, including explicit ownerless rules."""

    def __init__(self, path: Path) -> None:
        self.rules = []
        for line in path.read_text().splitlines():
            fields = line.split("#", 1)[0].split()
            if not fields:
                continue
            pattern, *owners = fields
            if any(re.fullmatch(r"@[A-Za-z0-9-]+", owner) is None for owner in owners):
                raise ValueError("unsupported CODEOWNERS owner")
            self.rules.append((_pattern(pattern), set(owners)))
        if not self.rules:
            raise ValueError("CODEOWNERS has no active rules")

    def owners(self, filepath: str) -> set[str]:
        owners = set()
        for pattern, candidates in self.rules:
            if pattern.search(filepath):
                owners = candidates
        return set(owners)


def build_codeowners(repo_root, source):
    """Read the policy's repository-relative path from the trusted checkout."""
    path = repo_root / source.path
    if not path.resolve().is_relative_to(repo_root.resolve()):
        raise ValueError("CODEOWNERS must stay inside the trusted checkout")
    return CodeownersResolver(path)
