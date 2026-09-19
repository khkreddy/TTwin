#!/bin/bash
# Push Science 6–8 CANDIDATE artifacts only. Never live question JSON, never full map blobs.
set -euo pipefail
cd /home/harik/TTwin
if [ -x /tmp/github-ssh.sh ]; then
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-/tmp/github-ssh.sh}"
else
  export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -4 -i /home/harik/.ssh/id_ed25519 -o IdentitiesOnly=yes}"
fi

node tools/pack_g68_candidates.js >/dev/null
if [ -d candidate/math-middle_6_8/items ]; then
  TTWIN_G68_SUBJECT=maths node tools/pack_g68_candidates.js --maths >/dev/null || true
fi

git add \
  candidate/science-middle_6_8 \
  candidate/math-middle_6_8 \
  tools/modify_g68.js \
  tools/pack_g68_candidates.js \
  tools/push_g68_candidates.sh \
  tools/tests/test_modify_packet.js \
  tools/tests/test_modify_gates.js \
  tools/tests/test_modify_g68.js \
  tools/tests/test_g68_overlay.js \
  js/kimi.js

if git diff --cached --name-only | grep -E 'BIOLOGY_MAP|CHEMISTRY_MAP_COMBINED|MATHEMATICS_MAP|PHYSICS_MAP'; then
  echo "refusing to commit full map blobs" >&2
  exit 1
fi
if git diff --cached --name-only | grep -E '^data/questions/'; then
  echo "refusing to merge candidates into the live question pool" >&2
  exit 1
fi

if git diff --cached --quiet; then
  echo "no-op: nothing staged for CANDIDATE push"
  git log -1 --oneline
  git ls-remote origin refs/heads/main | awk '{print $1}'
  exit 0
fi

n=$(find candidate/science-middle_6_8/items -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
git commit -m "Add Science 6–8 CANDIDATE items (${n} unverified, not live)"
git push origin main
git log -1 --oneline
git ls-remote origin refs/heads/main | awk '{print $1}'
