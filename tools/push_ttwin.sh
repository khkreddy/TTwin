#!/bin/bash
set -euo pipefail
cd /home/harik/TTwin
if [ -x /tmp/github-ssh.sh ]; then
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-/tmp/github-ssh.sh}"
else
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -4 -i /home/harik/.ssh/id_ed25519 -o IdentitiesOnly=yes}"
fi
git add data/questions data/nav data/meta.json data/subjects.json data/schema \
  data/held_questions.jsonl data/held_questions_summary.json \
  tools js css index.html
if git diff --cached --quiet; then
  echo "no-op: working tree clean for pack files"
  git log -1 --oneline
  git ls-remote origin refs/heads/main | awk '{print $1}'
  exit 0
fi
git commit -m "Pack exam-complete non-MCQ questions under ttwin.question.v1"
git push origin main
git log -1 --oneline
git ls-remote origin refs/heads/main | awk '{print $1}'
