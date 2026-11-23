#!/bin/bash
# Rebuild the Omarchy fork's carried changes on the latest Omarchy, in a throwaway worktree, and say what still applies.
# Usage: tools/check_fork.sh FORK_CHECKOUT [PULL_REQUEST...]    (default: 13212 16608 17648, each tried alone)
set -euo pipefail
fork=${1:?fork checkout}; shift || true; prs=("$@"); (( ${#prs[@]} )) || prs=(13212 16608 17648)
git -C "$fork" fetch -q upstream quattro; bad=0; base=$(git -C "$fork" rev-parse upstream/quattro); echo "Omarchy at ${base:0:9}"
for p in "${prs[@]}"; do
  git -C "$fork" fetch -q upstream "+pull/$p/head:refs/pr/$p"
  if git -C "$fork" merge-tree --write-tree "$base" "refs/pr/$p" >/dev/null 2>&1; then echo "$p applies"; else echo "$p CONFLICTS"; bad=1; fi
done
exit $bad
