#!/bin/bash
# Push the current branch. Refuses main and master.
set -euo pipefail
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  echo "refusing to push $branch" >&2
  exit 1
fi
git push -u origin "$branch"
