set -euo pipefail

body="$RUNNER_TEMP/linkmortem-issue.md"
cp "$REPORT" "$body"
case "$PULL_REQUEST_STATUS" in
  conflict) printf '\nLinkmortem had proven replacements, but the patch no longer applies to the default branch, so no pull request was opened this week.\n' >> "$body" ;;
  edited-by-people) printf '\nSomeone pushed to the linkmortem/rest branch, so Linkmortem left it alone this week.\n' >> "$body" ;;
esac
if [ -n "$PULL_REQUEST" ]; then
  printf '\nThe replacements Linkmortem could prove are waiting for review in %s\n' "$PULL_REQUEST" >> "$body"
fi

existing=$(gh issue list --state open --search "\"$TITLE\" in:title" --json number --jq '.[0].number // empty')
if [ -n "$existing" ]; then
  gh issue comment "$existing" --body-file "$body"
else
  gh issue create --title "$TITLE" --body-file "$body"
fi
