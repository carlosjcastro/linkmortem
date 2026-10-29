set -euo pipefail

ghosts_in() {
  grep -oP '^- `\K[^`]+' | sort -u || true
}

existing=$(gh issue list --state open --search "\"$TITLE\" in:title" --json number --jq '.[0].number // empty')

if [ "$GHOSTS" = "0" ]; then
  if [ -n "$existing" ]; then
    gh issue comment "$existing" --body "Linkmortem found no dead links in the latest scan. Every ghost has been laid to rest, so this issue is closing."
    gh issue close "$existing" --reason completed
  fi
  exit 0
fi

body="$RUNNER_TEMP/linkmortem-issue.md"
cp "$REPORT" "$body"
case "$PULL_REQUEST_STATUS" in
  conflict) printf '\nLinkmortem had proven replacements, but the patch no longer applies to the default branch, so no pull request was opened this time.\n' >> "$body" ;;
  edited-by-people) printf '\nSomeone pushed to the linkmortem/rest branch, so Linkmortem left it alone this time.\n' >> "$body" ;;
esac
if [ -n "$PULL_REQUEST" ]; then
  printf '\nThe replacements Linkmortem could prove are waiting for review in %s\n' "$PULL_REQUEST" >> "$body"
fi

if [ -z "$existing" ]; then
  gh issue create --title "$TITLE" --body-file "$body"
  exit 0
fi

before=$(gh issue view "$existing" --json body --jq .body | ghosts_in)
after=$(ghosts_in < "$REPORT")
gh issue edit "$existing" --body-file "$body" > /dev/null
appeared=$(comm -13 <(echo "$before") <(echo "$after") | sed '/^$/d')
rested=$(comm -23 <(echo "$before") <(echo "$after") | sed '/^$/d')
if [ -z "$appeared$rested" ]; then
  exit 0
fi

update="$RUNNER_TEMP/linkmortem-update.md"
: > "$update"
if [ -n "$appeared" ]; then
  printf 'New dead links since the last scan:\n\n%s\n' "$(sed 's/.*/- `&`/' <<< "$appeared")" >> "$update"
fi
if [ -n "$rested" ]; then
  printf '\nLaid to rest since the last scan:\n\n%s\n' "$(sed 's/.*/- `&`/' <<< "$rested")" >> "$update"
fi
printf '\nThe issue description always holds the latest full report.\n' >> "$update"
gh issue comment "$existing" --body-file "$update"
