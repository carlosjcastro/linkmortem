set -euo pipefail

branch="linkmortem/rest"
bot_email="41898282+github-actions[bot]@users.noreply.github.com"
title="Replace dead links found by Linkmortem"

finish() {
  echo "pull-request-status=$1" >> "$GITHUB_OUTPUT"
  echo "pull-request=${2:-}" >> "$GITHUB_OUTPUT"
  printf '\nPull request: %s %s\n' "$1" "${2:-}" >> "$GITHUB_STEP_SUMMARY"
  exit 0
}

base=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
git config user.name "github-actions[bot]"
git config user.email "$bot_email"
git switch --quiet -C "$branch"

git apply --check "$PATCH" 2>/dev/null || finish conflict
git apply "$PATCH"
git commit --quiet --all --message "fix: replace dead links found by Linkmortem"

if git fetch --quiet origin "$branch" 2>/dev/null; then
  [ "$(git log -1 --format=%ae FETCH_HEAD)" = "$bot_email" ] || finish edited-by-people
  if git diff --quiet FETCH_HEAD HEAD; then
    current=$(gh pr list --head "$branch" --state open --json url --jq '.[0].url // empty')
    if [ -n "$current" ]; then
      gh pr edit "$current" --body-file "$BODY" > /dev/null
    fi
    finish unchanged "$current"
  fi
fi

git push --quiet --force origin "$branch"
existing=$(gh pr list --head "$branch" --state open --json url --jq '.[0].url // empty')
if [ -n "$existing" ]; then
  gh pr edit "$existing" --body-file "$BODY" > /dev/null
  finish updated "$existing"
fi
finish opened "$(gh pr create --base "$base" --head "$branch" --title "$title" --body-file "$BODY")"
