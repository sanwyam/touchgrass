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


def roast(commits, savage=False):
    def pick(mild, spicy):
        return spicy if savage else mild

    n = len(commits)
    out = [f"📊 {n} commits analyzed. let's begin.\n"]

    # late night commits (midnight to 5am)
    late = sum(1 for d, _ in commits if d.hour < 5)
    if late:
        out.append(pick(
            f"🌙 {late} commits between 12am and 5am. sleep is free, you know.",
            f"🌙 {late} commits between 12am and 5am. your pillow filed a missing person report."))

    # lazy messages
    lazy = sum(1 for _, m in commits if m.lower().strip(".! ") in LAZY)
    if lazy:
        out.append(pick(
            f"💬 {lazy} commit messages were basically 'fix' or 'update'. future you has no idea what happened here.",
            f"💬 {lazy} commit messages were 'fix' or 'update'. fix WHAT. update WHERE. use your words."))

    # commit message length
    avg = sum(len(m) for _, m in commits) / n
    if avg < 20:
        out.append(pick(
            f"✍️ average commit message: {avg:.0f} characters. a text to your crush has more effort.",
            f"✍️ average commit message: {avg:.0f} characters. a fortune cookie has more depth."))
    longest = max((m for _, m in commits), key=len)
    if len(longest) > 72:
        out.append(f"📜 one commit message is {len(longest)} characters. that's a diary entry, not a commit.")

    # weekend warrior
    weekend = sum(1 for d, _ in commits if d.weekday() >= 5)
    out.append(pick(
        f"📅 {weekend} weekend commits ({weekend * 100 // n}%). touch grass challenge: failed.",
        f"📅 {weekend} weekend commits ({weekend * 100 // n}%). the grass is filing a restraining order."))

    # most repeated message
    msg, count = Counter(m for _, m in commits).most_common(1)[0]
    if count > 1:
        out.append(pick(
            f"🔁 you wrote '{msg}' {count} times. creativity: missing.",
            f"🔁 you wrote '{msg}' {count} times. copy-paste is not a personality."))

    # busiest hour
    hour, _ = Counter(d.hour for d, _ in commits).most_common(1)[0]
    out.append(f"⏰ peak commit hour: {hour:02d}:00. the people who know you know why.")

    # longest gap
    days = sorted(d for d, _ in commits)
    gap = max((b - a).days for a, b in zip(days, days[1:])) if n > 1 else 0
    if gap > 14:
        out.append(pick(
            f"👻 longest disappearance: {gap} days. the repo thought you left it.",
            f"👻 longest disappearance: {gap} days. the repo has moved on and started seeing other developers."))

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Roast your git history.")
    parser.add_argument("repo", nargs="?", default=".",
                        help="path to a git repo (default: current folder)")
    parser.add_argument("--savage", action="store_true",
                        help="turn the roasts up to 11")
    args = parser.parse_args()
    commits = get_commits(args.repo)
    if not commits:
        sys.exit("no commits found. nothing to roast, which is its own roast.")
    print(roast(commits, args.savage))


if __name__ == "__main__":
    main()