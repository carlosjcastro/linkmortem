export const WATCH_WORKFLOW = `name: Linkmortem

on:
  workflow_dispatch:
  schedule:
    - cron: "17 9 * * 1"

permissions:
  contents: read

jobs:
  links:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v7
      - uses: carlosjcastro/linkmortem@main
        with:
          backboard-api-key: \${{ secrets.BACKBOARD_API_KEY }}
          serpapi-api-key: \${{ secrets.SERPAPI_API_KEY }}
          open-pull-request: "true"
          open-issue: "true"
`;
