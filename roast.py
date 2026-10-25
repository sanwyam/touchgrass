"""commit-roaster: reads your git history and gently destroys you."""
import argparse
import subprocess
import sys
from collections import Counter
from datetime import datetime

LAZY = {"fix", "update", "changes", "wip", "test", "asdf", "stuff",
        "final", "commit", "oops", "idk", "."}


def get_commits(repo):
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", "--pretty=format:%aI%x1f%s"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit("not a git repo (or git isn't installed). bestie...")
    commits = []
    for line in out.splitlines():
        when, _, msg = line.partition("\x1f")
        commits.append((datetime.fromisoformat(when), msg.strip()))
    return commits


def roast(commits):
    n = len(commits)
    out = [f"📊 {n} commits analyzed. let's begin.\n"]

    # late night commits (midnight to 5am)
    late = sum(1 for d, _ in commits if d.hour < 5)
    if late:
        out.append(f"🌙 {late} commits between 12am and 5am. "
                   "sleep is free, you know.")

    # lazy messages
    lazy = sum(1 for _, m in commits if m.lower().strip(".! ") in LAZY)
    if lazy:
        out.append(f"💬 {lazy} commit messages were basically 'fix' or 'update'. "
                   "future you has no idea what happened here.")

    # weekend warrior
    weekend = sum(1 for d, _ in commits if d.weekday() >= 5)
    out.append(f"📅 {weekend} weekend commits ({weekend * 100 // n}%). "
               "touch grass challenge: failed.")

    # most repeated message
    msg, count = Counter(m for _, m in commits).most_common(1)[0]
    if count > 1:
        out.append(f"🔁 you wrote '{msg}' {count} times. creativity: missing.")

    # busiest hour
    hour, _ = Counter(d.hour for d, _ in commits).most_common(1)[0]
    out.append(f"⏰ peak commit hour: {hour:02d}:00. "
               "the people who know you know why.")

    # longest gap
    days = sorted(d for d, _ in commits)
    gap = max((b - a).days for a, b in zip(days, days[1:])) if n > 1 else 0
    if gap > 14:
        out.append(f"👻 longest disappearance: {gap} days. "
                   "the repo thought you left it.")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Roast your git history.")
    parser.add_argument("repo", nargs="?", default=".",
                        help="path to a git repo (default: current folder)")
    args = parser.parse_args()
    commits = get_commits(args.repo)
    if not commits:
        sys.exit("no commits found. nothing to roast, which is its own roast.")
    print(roast(commits))


if __name__ == "__main__":
    main()