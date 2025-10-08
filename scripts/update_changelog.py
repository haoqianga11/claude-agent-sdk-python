#!/usr/bin/env python3
"""Update CHANGELOG.md with a new version entry based on git commits."""

import sys
import subprocess
import re
from pathlib import Path
from collections import defaultdict


def get_commits_since_tag(previous_tag: str | None) -> list[str]:
    """Get commit messages since the previous tag."""
    if previous_tag:
        cmd = ["git", "log", "--oneline", f"{previous_tag}..HEAD"]
    else:
        cmd = ["git", "log", "--oneline"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [line for line in result.stdout.strip().split("\n") if line]


def parse_commit(commit_line: str) -> tuple[str, str, str]:
    """Parse a commit line into (hash, type, message).

    Returns (hash, type, message) where type is one of:
    - feat: New features
    - fix: Bug fixes
    - docs: Documentation changes
    - chore: Maintenance tasks
    - refactor: Code refactoring
    - test: Test changes
    - other: Everything else
    """
    match = re.match(r"^(\w+)\s+(.*)$", commit_line)
    if not match:
        return "", "other", commit_line

    commit_hash = match.group(1)
    message = match.group(2)

    # Skip version bump commits
    if message.startswith("chore: bump version"):
        return commit_hash, "skip", message

    # Detect commit type from conventional commit format
    if message.startswith("feat:") or message.startswith("feat("):
        return commit_hash, "feat", message.split(":", 1)[1].strip()
    elif message.startswith("fix:") or message.startswith("fix("):
        return commit_hash, "fix", message.split(":", 1)[1].strip()
    elif message.startswith("docs:") or message.startswith("docs("):
        return commit_hash, "docs", message.split(":", 1)[1].strip()
    elif message.startswith("refactor:") or message.startswith("refactor("):
        return commit_hash, "refactor", message.split(":", 1)[1].strip()
    elif message.startswith("test:") or message.startswith("test("):
        return commit_hash, "test", message.split(":", 1)[1].strip()
    elif message.startswith("chore:") or message.startswith("chore("):
        return commit_hash, "chore", message.split(":", 1)[1].strip()
    else:
        # For non-conventional commits, try to infer from message
        msg_lower = message.lower()
        if any(word in msg_lower for word in ["fix", "fixes", "fixed", "bugfix"]):
            return commit_hash, "fix", message
        elif any(word in msg_lower for word in ["add", "adds", "added", "new", "support"]):
            return commit_hash, "feat", message
        elif any(word in msg_lower for word in ["update", "updates", "updated", "improve"]):
            return commit_hash, "improvement", message
        else:
            return commit_hash, "other", message


def generate_changelog_entry(version: str, previous_tag: str | None) -> str:
    """Generate a changelog entry for the given version."""
    commits = get_commits_since_tag(previous_tag)

    if not commits:
        return f"## {version}\n\nNo changes.\n"

    # Group commits by type
    grouped: dict[str, list[str]] = defaultdict(list)
    for commit_line in commits:
        commit_hash, commit_type, message = parse_commit(commit_line)
        if commit_type != "skip":
            grouped[commit_type].append(message)

    # Build changelog entry
    entry_lines = [f"## {version}\n"]

    # New features
    if "feat" in grouped:
        entry_lines.append("### New Features\n")
        for msg in grouped["feat"]:
            entry_lines.append(f"- {msg}")
        entry_lines.append("")

    # Bug fixes
    if "fix" in grouped:
        entry_lines.append("### Bug Fixes\n")
        for msg in grouped["fix"]:
            entry_lines.append(f"- {msg}")
        entry_lines.append("")

    # Improvements
    if "improvement" in grouped or "refactor" in grouped:
        entry_lines.append("### Improvements\n")
        for msg in grouped.get("improvement", []) + grouped.get("refactor", []):
            entry_lines.append(f"- {msg}")
        entry_lines.append("")

    # Documentation
    if "docs" in grouped:
        entry_lines.append("### Documentation\n")
        for msg in grouped["docs"]:
            entry_lines.append(f"- {msg}")
        entry_lines.append("")

    # Other changes
    other_changes = (
        grouped.get("chore", []) +
        grouped.get("test", []) +
        grouped.get("other", [])
    )
    if other_changes:
        entry_lines.append("### Other Changes\n")
        for msg in other_changes:
            entry_lines.append(f"- {msg}")
        entry_lines.append("")

    return "\n".join(entry_lines)


def update_changelog(version: str, previous_tag: str | None) -> None:
    """Update CHANGELOG.md with a new version entry."""
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print("Error: CHANGELOG.md not found")
        sys.exit(1)

    content = changelog_path.read_text()

    # Generate new entry
    new_entry = generate_changelog_entry(version, previous_tag)

    # Insert after "# Changelog" header
    if "# Changelog" not in content:
        print("Error: CHANGELOG.md does not contain '# Changelog' header")
        sys.exit(1)

    # Split at the header and insert new entry
    parts = content.split("# Changelog\n", 1)
    if len(parts) != 2:
        print("Error: Could not split CHANGELOG.md at '# Changelog' header")
        sys.exit(1)

    updated_content = f"{parts[0]}# Changelog\n\n{new_entry}\n{parts[1]}"

    changelog_path.write_text(updated_content)
    print(f"Updated CHANGELOG.md with version {version}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python scripts/update_changelog.py <version> [previous_tag]")
        print("Example: python scripts/update_changelog.py 0.1.2 v0.1.1")
        sys.exit(1)

    version = sys.argv[1]
    previous_tag = sys.argv[2] if len(sys.argv) > 2 else None

    update_changelog(version, previous_tag)


if __name__ == "__main__":
    main()
