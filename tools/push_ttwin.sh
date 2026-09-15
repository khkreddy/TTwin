#!/bin/bash
set -euo pipefail
cd /home/harik/TTwin
export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-/tmp/github-ssh.sh}"
python3 tools/census_lbs.py /tmp/grok-goal-b0d4c3107c39/implementer/corpus_census.json >/dev/null
git add data/questions data/overlay data/meta.json data/schema tools js css index.html DEPLOYMENT_WIKI.md harness
if git diff --cached --quiet; then
  echo "no-op: working tree clean for pack files"
  git log -1 --oneline
  git ls-remote origin refs/heads/main | awk '{print $1}'
  exit 0
fi
git commit -m "Corpus LBS + Mx modify-seed overlay (pack-time, freeze untouched)"
git push origin main
git log -1 --oneline
git ls-remote origin refs/heads/main | awk '{print $1}'
