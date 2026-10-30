![The Linkmortem home page with a ghost made of light](docs/screenshots/linkmortem.jpg)

# Linkmortem

**Every dead link is a ghost.** Linkmortem finds the dead links and dead sections in a website or in the Markdown docs of a GitHub repository, works out why each one died, recovers what the page said from the Internet Archive, finds where the content lives now and writes the fix. Code decides everything it can verify. Gemma 4, an open weights model, reads only the pages code can't judge.

[![Live at linkmortem.tech](https://img.shields.io/badge/live-linkmortem.tech-E8A33D?style=for-the-badge)](https://linkmortem.tech)
[![Demo video on YouTube](https://img.shields.io/badge/demo_video-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/lp0didvo9Rs)
[![Example autopsy](https://img.shields.io/badge/example-autopsy-6E56CF?style=for-the-badge)](https://linkmortem.tech/r/n1piOyPEcD1E)

[![GitHub Action demo, pull request opened by the Action](https://img.shields.io/badge/Action_demo-pull_request_%231-238636?style=for-the-badge&logo=github)](https://github.com/carlosjcastro/linkmortem-playground/pull/1)
[![GitHub Action demo, issue kept by the Action](https://img.shields.io/badge/Action_demo-issue_%232-238636?style=for-the-badge&logo=github)](https://github.com/carlosjcastro/linkmortem-playground/issues/2)
[![CI status](https://img.shields.io/github/actions/workflow/status/carlosjcastro/linkmortem/ci.yml?branch=main&style=for-the-badge&label=CI&logo=githubactions&logoColor=white)](https://github.com/carlosjcastro/linkmortem/actions/workflows/ci.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-3DA639?style=for-the-badge)](LICENSE)

[![Built for the DEV Hacktoberfest 2026 Open Source AI Challenge, Week 4, Ghost in the Machine](https://img.shields.io/badge/DEV_Hacktoberfest_2026-Week_4%2C_Ghost_in_the_Machine-0A0A0A?style=for-the-badge&logo=devdotto&logoColor=white)](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)

## Contents

- [Why it exists](#why-it-exists)
- [The autopsy](#the-autopsy)
- [What makes it different](#what-makes-it-different)
- [Use it on the web](#use-it-on-the-web)
- [Use it as a GitHub Action](#use-it-as-a-github-action)
- [Use it from the command line](#use-it-from-the-command-line)
- [What every result means](#what-every-result-means)
- [Open models, measured](#open-models-measured)
- [Watching the agent work](#watching-the-agent-work)
- [How it's built](#how-its-built)
- [Challenge categories](#challenge-categories)
- [Security](#security)
- [Accessibility and design](#accessibility-and-design)
- [Limits](#limits)
- [Run it locally](#run-it-locally)
- [Configuration](#configuration)
- [Deploy](#deploy)
- [Built with AI](#built-with-ai)
- [Credits](#credits)
- [License](#license)

## Why it exists

The web forgets faster than we think. [38% of the web pages that existed in 2013 were gone ten years later](https://blog.archive.org/2026/04/23/gone-but-not-forgotten-recovering-the-dead-web/) (Pew Research Center, 2024), and 72% of the links in New York Times articles from 1998 no longer work (Zittrain and colleagues, 2021). When GeoCities went dark on October 26, 2009, millions of personal pages disappeared overnight, and every link that pointed to them turned into a ghost.

Most link checkers stop at "404". That leaves three problems unsolved:

- **Many dead pages don't say they're dead.** A parked domain, a soft 404 that answers 200, a redirect to an unrelated home page or an empty placeholder all pass a status check.
- **A list of broken links isn't a fix.** Someone still has to find what the page said and where it lives now.
- **The past is recoverable.** The Internet Archive keeps copies of most of these pages, and it can save the living ones before they die too.

Linkmortem treats each dead link the way a coroner treats a body. It names the cause of death with evidence, recovers the last healthy memory, looks for a reincarnation, lays the link to rest with a patch and preserves the living. In the spirit of the Day of the Dead, it honors the pages that are gone instead of just counting them.

## The autopsy

Every scan follows the same six steps, and each one reports what it did.

![The six steps of an autopsy on the home page](docs/screenshots/home-steps.png)

1. **Find.** Collects up to 150 links from up to 12 pages of a site, or from up to 40 Markdown files of a public repository at an exact branch, tag or commit. Relative links are resolved against the repository, badges and placeholder hosts like `example.com` are skipped, and links inside code blocks are ignored. When a limit cuts the scan short, the results say how many links were found and how many files or pages were read.
2. **Diagnose.** Checks each link and names its cause of death: not found, removed on purpose, dead domain, parked domain, error page in disguise, empty placeholder, unrelated redirect or missing section. Redirects and meta refresh are followed, and every hop goes through the same safety guard. A failure that may be temporary (429, 5xx, a network error, a DNS hiccup) is retried once before any verdict. Bot checks, login walls and pages that only render with JavaScript are reported as unconfirmed, never as dead.
3. **Remember.** Finds the last healthy copy in the Wayback Machine. Captures that are themselves error pages, parked domains or impossible dates are skipped, and links that already point to an archive don't look for a memory of themselves.
4. **Reincarnate.** Looks for where the content lives now, in this order: a new address the archived page itself announced, the graveyard of links Linkmortem already resolved, and a live web search. Gemma compares each candidate with the archived copy and decides whether it is the same page, a newer version or something else. Scrapers and lookalikes don't count.
5. **Rest.** Builds a `git apply` patch that replaces each dead link with its proven new home, or with its last healthy archived copy when there is no new home. From the GitHub Action, the patch becomes one pull request.
6. **Preserve.** Asks the Internet Archive to save up to 10 living links that weren't saved this month, before they become ghosts too.

![Results of a scan, with the verdict, coverage and the haunted house](docs/screenshots/results-verdict-house.png)

## What makes it different

### The model proposes, the code decides

Anything code can verify is decided by code: HTTP status, DNS, parked domains, bot checks, meta refresh, candidate relevance, document sections and announced moves. Gemma only judges what code can't read, such as a page that answers 200 but says "this content no longer exists". A link is a ghost only with evidence, and unreadable content is never evidence of death.

In production, Gemma is called for roughly one link in ten. One night of scans checked 301 links with only 30 calls to Gemma, for a total of USD 0.00141.

A real example shows the split. The TypeScript home page contains a code sample with the error `Property 'name' does not exist on type…`. "does not exist" is one of the phrases code treats as suspicious, because it usually means a page answers 200 but its content is gone. Code can't tell a sentence about a dead page from an example inside a code block, so it asks Gemma. Gemma read the page and answered `alive`. If Gemma hadn't been available, the link would have stayed unconfirmed, never dead.

<p>
  <img src="docs/screenshots/sentry-gemma-call.png" alt="A Gemma call in Sentry with the TypeScript page as input" width="49%">
  <img src="docs/screenshots/sentry-gemma-output.png" alt="Gemma's answer in Sentry, alive with the page title as evidence" width="49%">
</p>

Pages from the internet are fenced as data in every prompt. One of the pages scanned while building Linkmortem opens with "Ignore all previous instructions" to trap AI crawlers. Gemma kept classifying it, and Linkmortem even found the article at its new address.

![Another Gemma call in Sentry, with the prompt that fences the page as data](docs/screenshots/sentry-gemma-call-2.png)

### The page lives, but the section died

The most common break in documentation and awesome lists is a renamed heading. The page still answers 200, so most checkers call the link alive, but `README.md#install` points to a section that no longer exists. Linkmortem computes the anchors of every Markdown file the way GitHub does (ATX and Setext headings, HTML anchors, badges and link syntax stripped out), detects links to sections that are gone and proposes the closest heading in the same document. No model call is needed.

Calibrated against 427 section links in 7 real awesome lists, it found 0 false ghosts. In production it caught `#image` in [sorrycc/awesome-javascript](https://github.com/sorrycc/awesome-javascript), whose heading is now `#images`.

![A dead section with the closest heading proposed as its replacement](docs/screenshots/results-dead-section.png)

### The dead page said where it went

Some archived pages announce their own move. The last healthy copy of `airbnb.io/enzyme/index.html` says "Enzyme has moved. Redirecting now to enzymejs.github.io", while the live address now sends readers to an unrelated blog. Before spending a web search, Linkmortem reads the archived text for phrases like "has moved to", "moved permanently to" or "redirecting now to". It tries the same path on the new domain first, then its root, and accepts the address only if it is alive and not parked. The result is `enzymejs.github.io/enzyme/index.html`, "Introduction · Enzyme", found with no model call and no search. The interface, the report and the pull request all say the archived page announced the move.

![Enzyme's dead link, its memory and the new home the archived page announced](docs/screenshots/results-announced-move.png)

### Honest about what it did and didn't do

Linkmortem never claims more than it knows.

- **Coverage.** "Linkmortem checked the first 150 of the 887 links it found" and "It read 12 of the 40 Markdown files it could reach" appear in the interface, the report, the issue and the pull request.
- **Unconfirmed is its own verdict.** Bot checks, login walls and timeouts are listed under "Could not confirm", with the reason, and are never patched.
- **When Gemma isn't available,** suspicious pages stay unconfirmed and the results say how many and why. From the Action, the report explains how to set `backboard-api-key`.
- **Empty scans say why.** A site that builds its pages with JavaScript, a start page that couldn't be opened and a page that truly has no links get three different messages.
- **Searches have a daily budget.** When it runs out, results say so and point to the archived copy, instead of showing a failed search.
- **A shared autopsy says it is loading saved results,** "Nothing is being scanned again", and an expired one explains that autopsies last 30 days and how to scan again.
- **Copying never fails silently.** If the browser refuses, the page says so and opens the text to copy by hand.

<p>
  <img src="docs/screenshots/results-unconfirmed.png" alt="Could not confirm, with npmjs.com hidden behind a bot check" width="49%">
  <img src="docs/screenshots/results-loading.png" alt="The waiting ghost while a shared autopsy loads" width="49%">
</p>

![An expired or wrong autopsy link, with an honest title and how to scan again](docs/screenshots/results-not-found.png)

### Fixes a maintainer can trust

- Only proven replacements are written: a new home Gemma judged as the same page or its successor, a move the archived page announced, the closest heading of a moved section, or the last healthy archived copy with its date.
- Whole links only, so fixing `https://old.dev/a` never touches `https://old.dev/abc`.
- Code blocks and inline code are never rewritten, and relative links are only rewritten where they are the target of a link.
- The same dead link found in several files is fixed in all of them.

![The patch replacing a dead section and Enzyme's dead link](docs/screenshots/patch-diff.png)

## Use it on the web

Paste a website or a public GitHub repository at [linkmortem.tech](https://linkmortem.tech), or try the demo repository in one click. A repository can point at a branch, tag or commit with `/tree/<ref>`.

While the scan runs, progress says what is happening ("Checked 116 of 150 links", searching the Wayback Machine, looking for new homes) and ghosts appear as they are found. When it ends, the results read from top to bottom:

- **The verdict and three numbers,** dead, couldn't confirm and still alive, each a link to its section, plus the coverage note.
- **The haunted house.** The windows light up in proportion to the living links (lit is alive, flickering is unconfirmed, dark is dead) and every dead link rests in a grave with its ghost, up to 12 graves. Hovering a ghost shows its link, and selecting it jumps to its autopsy.
- **What you can do now,** in numbered steps:
  1. **Lay these links to rest.** Download the patch and apply it with `git apply linkmortem.patch`.
  2. **Preserve the living.** Send up to 10 living links to the Internet Archive and follow each one ("Saving", "Already saved recently", "Not saved" with the reason). Each autopsy can be preserved once.
  3. **Keep watching this repository.** For repositories, the workflow below is ready to copy.
  4. **Share this autopsy.** Results live for 30 days at `linkmortem.tech/r/<id>`. The link preview names the ghosts found, and shared pages are kept out of search engines so they never leave dead links behind when they expire.
- **One mini autopsy per ghost,** with the cause of death and its evidence, every file where the link appears, the memory with its date and excerpt, and the afterlife.
- **Could not confirm** and **Still alive,** collapsed below.

![What you can do now, with the patch, preservation, the workflow and the share link](docs/screenshots/results-next-steps.png)

<p>
  <img src="docs/screenshots/results-house-hover.png" alt="Hovering a ghost in the haunted house shows its link" width="49%">
  <img src="docs/screenshots/results-preserve.png" alt="Living links sent to the Internet Archive with their status" width="49%">
</p>

![The link preview of a shared autopsy, naming the ghosts found](docs/screenshots/share-preview.png)

The interface is in English and Spanish and always starts in English. The header switch changes the language, and the animations switch stops every animation.

## Use it as a GitHub Action

Scan the Markdown of a repository every week, keep one issue with the latest report and open one pull request with the replacements Linkmortem can prove.

```yaml
name: Linkmortem

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
          backboard-api-key: ${{ secrets.BACKBOARD_API_KEY }}
          serpapi-api-key: ${{ secrets.SERPAPI_API_KEY }}
          open-pull-request: "true"
          open-issue: "true"
```

Save it as `.github/workflows/linkmortem.yml`, add the secrets you have and enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**. Without any key, the code checks still run.

| Input               | Default                     | What it does                                                                                                                  |
| ------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `repository`        | the current repository      | Repository to scan, as `owner/name`                                                                                           |
| `ref`               | the commit being run        | Branch, tag or commit to scan                                                                                                 |
| `github-token`      | `github.token`              | Reads the repository through the GitHub API                                                                                   |
| `backboard-api-key` | empty                       | Lets Gemma judge suspicious pages through Backboard. Without it, code checks still run                                        |
| `backboard-model`   | `google/gemma-4-26b-a4b-it` | Model served by Backboard                                                                                                     |
| `serpapi-api-key`   | empty                       | Looks for where dead pages live now                                                                                           |
| `fail-on-ghosts`    | `false`                     | Fails the step when ghosts are found                                                                                          |
| `open-pull-request` | `false`                     | Opens or updates one pull request with the proven replacements                                                                |
| `open-issue`        | `false`                     | Keeps one issue with the latest report, comments only when ghosts appear or are laid to rest and closes it when none are left |

| Output                | Meaning                                                            |
| --------------------- | ------------------------------------------------------------------ |
| `ghosts`              | Number of dead links                                               |
| `unknown`             | Number of links that could not be confirmed                        |
| `report`              | Path to the Markdown report                                        |
| `replacements`        | Number of dead links with a proven replacement in the patch        |
| `pull-request`        | Address of the Linkmortem pull request, when there is one          |
| `pull-request-status` | `opened`, `updated`, `unchanged`, `conflict` or `edited-by-people` |

The job summary shows the report, followed by a line for the pull request and another for the issue (`opened`, `updated` or `closed`, with its link).

**The pull request** is careful by design:

- One pull request on the `linkmortem/rest` branch, updated instead of duplicated. When the patch didn't change, the branch is left alone, but the description is refreshed with the latest report.
- It never forces a patch that no longer applies, never overwrites a branch someone edited, never reopens a closed pull request and never merges.
- The description is a numbered list that fits any screen: the link as written in the file, its replacement, why it died and what backs the new link.

<p>
  <img src="docs/screenshots/playground-pull-request.png" alt="The pull request the Action opened in the playground, as a list" width="49%">
  <img src="docs/screenshots/playground-pull-request-diff.png" alt="The files changed in that pull request" width="49%">
</p>

**The issue** keeps the full report, including the links without a proven replacement:

- Its description always holds the latest report and links the pull request.
- It comments only when ghosts appear or are laid to rest, so nothing new means no notification.
- It closes itself when the repository is clean.

<p>
  <img src="docs/screenshots/playground-issue.png" alt="The issue the Action keeps up to date in the playground" width="49%">
  <img src="docs/screenshots/playground-action-summary.png" alt="The job summary with the report, the pull request and the issue" width="49%">
</p>

This repository runs the Action on itself every Monday and on every pull request that touches Markdown. The [playground](https://github.com/carlosjcastro/linkmortem-playground) shows it working from another repository, with a renamed section (`#install` → `#installation`) and a retired Unity tutorial replaced by its copy from 2019.

## Use it from the command line

```
cd backend
python -m app.cli https://github.com/owner/repo --report report.md --patch linkmortem.patch
```

| Option             | What it does                                                                       |
| ------------------ | ---------------------------------------------------------------------------------- |
| `target`           | A website or a GitHub repository, optionally with `/tree/<ref>`                    |
| `--report`         | Where to write the Markdown report                                                 |
| `--patch`          | Writes a git patch with the proven replacements and a pull request body next to it |
| `--github-output`  | Appends the scan counts and file paths to this file                                |
| `--fail-on-ghosts` | Exits with code 1 when ghosts are found                                            |

## What every result means

| Cause                                        | Verdict     | How it's decided                                                                                   |
| -------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| Alive                                        | alive       | The page answers with readable content that matches the link                                       |
| Alive, though its content loads with scripts | alive       | The page answers but has no readable text, which is never evidence of death                        |
| The page no longer exists                    | ghost       | 404                                                                                                |
| The page was removed on purpose              | ghost       | 410                                                                                                |
| The domain no longer exists                  | ghost       | DNS fails, even after a retry                                                                      |
| The domain is parked or for sale             | ghost       | A parking host or a for sale phrase found by code, or Gemma reading a page made of ads             |
| An error page in disguise                    | ghost       | Gemma reads an error message on a page that answered 200                                           |
| An empty or unfinished page                  | ghost       | Gemma reads a placeholder, a default server page or a coming soon notice                           |
| Sends readers somewhere unrelated            | ghost       | The link redirects to a different site and Gemma reads unrelated content                           |
| The section no longer exists                 | ghost       | No heading or anchor in the document creates that section                                          |
| The server failed to answer                  | unconfirmed | 5xx, even after a retry                                                                            |
| Could not reach the server                   | unconfirmed | The connection failed                                                                              |
| The server took too long                     | unconfirmed | Timeout, even after a retry                                                                        |
| Hidden behind a login or bot check           | unconfirmed | 401, 403 or 429, a login wall, a bot check or a request to update the browser or enable JavaScript |
| Private address, not checked                 | unconfirmed | The address isn't public, so it's never requested                                                  |
| Gemma could not decide                       | unconfirmed | Gemma's answer wasn't usable                                                                       |
| Gemma wasn't available to read it            | unconfirmed | The model didn't answer                                                                            |

| Afterlife                            | Meaning                                                                          |
| ------------------------------------ | -------------------------------------------------------------------------------- |
| Reincarnated at a new address        | Same content at a new address, judged by Gemma or announced by the archived page |
| Lives on in a newer version          | A newer version of the same content, judged by Gemma                             |
| Closest section in the same document | The heading that replaced a renamed section                                      |
| Found in Linkmortem's graveyard      | A link already resolved in an earlier scan, found without a new web search       |
| No new home found                    | The archived copy is the best replacement                                        |
| The search didn't answer             | The search service failed this time                                              |
| Search limit reached                 | This scan used its 5 searches                                                    |
| Web searches used up for today       | The daily search budget ran out, and the archived copy still works               |

| Memory                            | Meaning                                                           |
| --------------------------------- | ----------------------------------------------------------------- |
| Last healthy copy, with its date  | A capture that isn't an error page, linked to the Wayback Machine |
| No healthy copy                   | The Wayback Machine never saved a healthy version                 |
| The Wayback Machine didn't answer | Try again in a few minutes                                        |

## Open models, measured

Choosing the model was itself an experiment. Linkmortem captured 60 prompts while scanning old repositories, labeled 55 of them (42 page classifications and 13 candidate comparisons) and replayed them against nine open weights models through a single Backboard API key. A costly error is calling a living page dead or accepting a different page as the new home, the two mistakes that hurt users most.

| Model                            | Accuracy | Costly errors | Median latency |
| -------------------------------- | -------- | ------------- | -------------- |
| Gemma 4 31B                      | 98%      | 0             | 2.98 s         |
| **Gemma 4 26B A4B (production)** | **95%**  | **0**         | **1.22 s**     |
| Llama 4 Scout (JSON by prompt)   | 93%      | 4             | 5.06 s         |
| DeepSeek V3.2                    | 91%      | 3             | 4.29 s         |
| Qwen3 30B A3B Instruct           | 91%      | 3             | 2.57 s         |
| Gemma 4 e4b, local with Ollama   | 87%      | 1             | 0.72 s         |
| Gemma 3 27B                      | 87%      | 5             | 2.48 s         |
| Ministral 14B                    | 79%      | 10            | 1.86 s         |
| Gemma 3 4B                       | 67%      | 10            | 1.29 s         |

What the numbers say:

- **Gemma 4 26B runs in production.** No costly errors, the fastest of the cloud models and less than half the input price of Gemma 4 31B.
- **The generational jump is real.** Gemma 3 27B made 5 costly errors, and Gemma 4 26B made none.
- **Accuracy isn't everything.** Llama 4 Scout beats DeepSeek and Qwen on accuracy but makes more costly errors, and Ministral's 79% hides 10 mistakes that would hurt users.
- **Local works too.** Gemma 4 e4b with Ollama reaches 87% with a single costly error in 0.72 s, for free.

The first run said Llama 4 Scout scored 0%. It had never answered: the provider rejected JSON mode and returned the error inside a successful response. Once the evaluation stored the reason for every invalid answer, the adapter learned to fall back to JSON requested by prompt, and Llama went from 0% to 93%.

Labels were proposed with AI help and reviewed by hand. Results vary by a few points between runs even at temperature 0. The full report, with invalid answers, p95 latency and tokens, is in [`backend/evals/REPORT.md`](backend/evals/REPORT.md).

To reproduce it, set `LINKMORTEM_CAPTURE_FILE` while scanning to record prompts, label them with `python -m evals.label <captured file>` and compare models with `python -m evals.compare <model> <model> …` (for example `backboard:openrouter:google/gemma-4-26b-a4b-it` or `ollama:gemma4:e4b`). The comparison rewrites `REPORT.md` with the models you pass.

## Watching the agent work

Every scan is traced in Sentry as an AI agent:

- `invoke_agent Linkmortem`, whose input is "Find the dead links in …" and whose output is the scan summary.
- `execute_tool` for each step: `diagnose_link`, `recall_memory`, `find_new_home`, `web_search`, `search_graveyard` and `preserve_page`.
- `gen_ai.chat` for each Gemma call, with the provider, model, tokens, cost, the system prompt, the page Gemma read and its answer.
- `gen_ai.evaluate` for each model in the comparison.

Sentry receives the prompts and answers built from public pages, but never IP addresses, cookies or request bodies.

### What the traces showed

- **How little the model is needed.** One night of production scans made 301 `diagnose_link` calls and only 30 Gemma calls, none failed. Gemma answered in 1.66 s on average and 3.27 s at P95, and those 30 calls used 12,927 tokens for USD 0.00141.
- **A score that was never earned.** The first model comparison gave Llama 4 Scout and Mistral Small 0%. Their traces had 165 errors and 0 tokens, so they had never answered. Backboard returned 200 with a provider error inside, because those servers rejected JSON mode. Asking for JSON in the prompt took Llama from 0% to 93%.
- **A span with no input.** The agent trace said "No input for this span". The agent never reported its task or its summary, and the deprecated `gen_ai.response.text` attribute was in use. Now the agent reports "Find the dead links in …" and its summary, and each Gemma call reports `gen_ai.input.messages` and `gen_ai.output.messages`.
- **Code suspects, Gemma decides.** The TypeScript home page reached Gemma because its code sample says "does not exist". The trace shows Gemma answering `alive` with the title as evidence.

<p>
  <img src="docs/screenshots/sentry-agent-input.png" alt="The agent's input in Sentry, the task it received" width="49%">
  <img src="docs/screenshots/sentry-agent-output.png" alt="The agent's output in Sentry, the scan summary" width="49%">
</p>

<p>
  <img src="docs/screenshots/sentry-agents-overview.png" alt="The AI agents overview in Sentry, filtered by production" width="49%">
  <img src="docs/screenshots/sentry-agents-overview-2.png" alt="More of the agents overview: model calls, tokens and cost" width="49%">
</p>

<p>
  <img src="docs/screenshots/sentry-agents-tools.png" alt="Every tool the agent calls, with calls, errors and duration" width="49%">
  <img src="docs/screenshots/sentry-agents-models.png" alt="Gemma 4 26B with its calls, tokens, cost and latency" width="49%">
</p>

![One scan as a trace: invoke_agent with its tools and Gemma calls](docs/screenshots/sentry-trace-waterfall.png)

<p>
  <img src="docs/screenshots/sentry-agent-transcript.png" alt="The agent transcript, with every Gemma call in order" width="49%">
  <img src="docs/screenshots/sentry-agent-transcript-2.png" alt="More of the transcript, with the pages Gemma read and its answers" width="49%">
</p>

Sentry shows prompts as HTML, so the `<page>` tags that fence the page text are hidden in its view. They are in the prompt, and a test checks it.

## How it's built

Where each piece runs and what it talks to. The same scanner runs on Render for the web and on the GitHub Actions runner for the Action.

```mermaid
flowchart LR
  browser["Browser<br/>React 19, Tailwind, Three.js"]

  subgraph render["Render, Docker, linkmortem.tech"]
    api["FastAPI<br/>address checks, 16 KB bodies,<br/>rate limit, security headers"]
  end

  subgraph runner["GitHub Actions runner"]
    action["Linkmortem Action<br/>on a schedule or on demand"]
    cli["Command line<br/>app.cli"]
  end

  scanner["Scanner, the same code in both<br/>find, diagnose, remember,<br/>reincarnate, rest"]

  subgraph open["Open pieces"]
    gemma["Gemma 4<br/>Backboard or Ollama"]
    wayback["Internet Archive<br/>Wayback Machine and Save Page Now"]
  end

  subgraph partners["Partner services"]
    serpapi["SerpApi<br/>live search"]
    atlas[("MongoDB Atlas<br/>autopsies, caches,<br/>vector graveyard")]
    sentry["Sentry<br/>agent traces"]
  end

  subgraph sources["What gets read"]
    githubapi["GitHub API<br/>and raw Markdown"]
    pages["Public web pages<br/>through the SSRF guard"]
  end

  subgraph results["What comes back"]
    autopsy["Autopsy and haunted house<br/>shared at /r/id"]
    patch["linkmortem.patch"]
    pr["Pull request and issue"]
  end

  browser -->|"POST /api/scans/stream"| api
  api --> scanner
  api -->|"NDJSON events"| autopsy
  action --> cli
  cli --> scanner
  scanner --> githubapi
  scanner --> pages
  scanner --> gemma
  scanner --> wayback
  scanner --> serpapi
  scanner <--> atlas
  scanner -.-> sentry
  api -->|"preserve living links"| wayback
  scanner --> patch
  patch -->|"scripts in the Action"| pr
```

How each link is decided, from the moment it's found to the fix. Every diamond is a decision made by code, and Gemma is asked only on the two paths that need reading.

```mermaid
flowchart TD
  link(["A link found in a page<br/>or a Markdown file"]) --> section{"Points to a section<br/>of a repository document?"}
  section -->|"yes"| anchor{"Does a heading or<br/>anchor create it?"}
  anchor -->|"yes"| alive(["Alive"])
  anchor -->|"no"| closest["Closest heading in the<br/>same document, no model"]
  section -->|"no"| fetch["Fetch through the safety guard<br/>follow redirects and meta refresh<br/>retry once if the failure may be temporary"]
  fetch --> code{"Can code decide?"}
  code -->|"404, 410, dead domain,<br/>parked domain"| ghost(["Ghost"])
  code -->|"5xx, timeout, login,<br/>bot check, private address"| unknown(["Could not confirm"])
  code -->|"healthy page, or text<br/>that only loads with scripts"| alive
  code -->|"readable page that<br/>looks dead"| gemma["Gemma 4 reads the page<br/>fenced as data"]
  gemma -->|"alive"| alive
  gemma -->|"error page, placeholder,<br/>parked or unrelated"| ghost
  gemma -->|"unusable or unavailable"| unknown
  ghost --> memory{"Healthy copy in the<br/>Wayback Machine?"}
  memory -->|"no"| listed(["Listed in the report<br/>without a replacement"])
  memory -->|"yes"| announced{"Does the archived page<br/>announce a new address?"}
  announced -->|"yes, and it is alive"| proven(["Proven replacement"])
  announced -->|"no"| known{"Known in the cache<br/>or the Atlas graveyard?"}
  known -->|"candidates"| compare["Gemma compares each candidate<br/>with the archived copy"]
  known -->|"nothing yet"| search["SerpApi search<br/>within 5 per scan and 20 per day"]
  search --> compare
  compare -->|"same page or newer version"| proven
  compare -->|"different, none or<br/>budget spent"| archived(["Last healthy archived<br/>copy as replacement"])
  closest --> proven
  proven --> deliver["Patch, pull request and issue"]
  archived --> deliver
```

| Piece                | Role                                                                                                                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gemma 4**          | Classifies suspicious pages and compares candidates for a new home. Local with Ollama or in the cloud                                                                                     |
| **Backboard**        | Serves Gemma in production and ran the comparison of nine open models with one API key                                                                                                    |
| **Internet Archive** | Wayback Machine for the last healthy copy, Save Page Now to preserve living links                                                                                                         |
| **SerpApi**          | Live web search for the new home of a dead page, with 5 searches per scan and a daily budget so one busy day can't spend the monthly quota                                                |
| **MongoDB Atlas**    | Shared autopsies for 30 days, a 7 day cache of memories and new homes, and a graveyard of resolved links with Vector Search and Automated Embedding that answers before spending a search |
| **Sentry**           | Agent tracing with prompts, answers, tokens and cost                                                                                                                                      |
| **GitHub Actions**   | CI with tests, Ruff and Prettier, the reusable Action, the weekly scan of this repository, the automatic pull request and the issue                                                       |
| **GitHub Copilot**   | The coding agent wrote the first security and contributing guides in [PR #3](https://github.com/carlosjcastro/linkmortem/pull/3), fixed after human review                                |
| **Render**           | Runs the API and the interface from a two stage Docker image at linkmortem.tech                                                                                                           |
| **Three.js**         | The ghost of 9,000 points with falling marigold petals on the home page, and the haunted house of each autopsy                                                                            |

The backend is Python 3.12 or newer with FastAPI, httpx2, Pydantic and PyMongo's async client, checked with Ruff and pytest (181 tests). The interface is React 19 with Vite, Tailwind CSS 4 and Three.js, formatted with Prettier and tested with Vitest (62 tests). Three.js loads in its own chunk only when a scene appears, so the home page shows up before it.

In production:

<p>
  <img src="docs/screenshots/render-service.png" alt="The Linkmortem service live on Render with its custom domain" width="49%">
  <img src="docs/screenshots/backboard-usage.png" alt="Gemma calls through Backboard, with tokens and cost per call" width="49%">
</p>

<p>
  <img src="docs/screenshots/atlas-collections.png" alt="The Linkmortem database in MongoDB Atlas with its collections" width="49%">
  <img src="docs/screenshots/atlas-vector-index.png" alt="The graveyard's Vector Search index, active" width="49%">
</p>

```
backend/
  app/scan/        finding links, sections, diagnosis and the safety guard
  app/memory/      the Wayback Machine
  app/afterlife/   announced moves, the graveyard, search and Gemma's comparison
  app/aftercare/   patches, pull request replacements and preservation
  app/report/      Markdown report, issue and pull request bodies
  app/llm/         Gemma through Ollama or Backboard, prompts fenced as data
  app/persistence/ autopsies, caches and the graveyard in Atlas
  evals/           the model comparison
frontend/src/
  features/        scan, results, aftercare, house, haunting, home, i18n, motion
  components/      header, navigation and the graveyard footer
scripts/           the pull request and issue steps of the Action
action.yml         the reusable GitHub Action
render.yaml        the Render Blueprint
```

## Challenge categories

Linkmortem enters every category it actually uses, and none it doesn't.

| Category                 | What the category asks                                                                      | How Linkmortem meets it                                                                                                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gemma**                | Use Gemma to build the project                                                              | Gemma 4 classifies suspicious pages and compares candidates for a new home. It runs locally with Ollama (`gemma4:e4b`) or in the cloud through Backboard (`gemma-4-26b-a4b-it`), and the evaluation shows why: 0 costly errors                                    |
| **Render**               | Use Render as the AI runtime or to host an agent's front end                                | Render runs the agent and its interface in production from a Docker image, with a health check and deploys only after CI passes                                                                                                                                   |
| **.tech Domain**         | Put the project live on a .tech domain claimed through Hacktoberfest                        | [linkmortem.tech](https://linkmortem.tech), with HTTPS, structured data, a sitemap and link previews                                                                                                                                                              |
| **Backboard**            | Compare open weights models through a single Backboard API key                              | Nine open models compared on 55 labeled cases with one key, a comparison that chose the production model. Backboard also serves Gemma in production                                                                                                               |
| **GitHub Copilot**       | Build with Copilot's coding agent, automate with GitHub Actions or review PRs with Copilot  | The coding agent resolved [issue #2](https://github.com/carlosjcastro/linkmortem/issues/2) in [PR #3](https://github.com/carlosjcastro/linkmortem/pull/3). GitHub Actions runs CI, the reusable Action, the weekly scan, the automatic pull request and the issue |
| **MongoDB Atlas**        | Use Atlas as the data layer, with Vector Search for retrieval                               | Atlas stores shared autopsies and caches, and the graveyard uses Vector Search with Automated Embedding (`voyage-4`) to find links already resolved before spending a search                                                                                      |
| **Sentry Agent Tracing** | Show the agent's work: setup, latency, tokens, cost, what you found and how you debugged it | Every scan is an `invoke_agent` trace with its tools and every Gemma call, with prompts, answers, tokens and cost. The traces exposed a model comparison that had never answered and a span with no input, as shown [above](#what-the-traces-showed)              |
| **SerpApi**              | Give an agent live web search                                                               | SerpApi finds where a dead page lives now, with a cap per scan and a daily budget                                                                                                                                                                                 |
| **ElevenLabs**           | Generate narration for the demo video                                                       | The [demo video](https://youtu.be/lp0didvo9Rs) is narrated with ElevenLabs                                                                                                                                                                                        |

## Security

- **The address you enter** is checked in the browser and again on the server: `http` or `https` only, up to 300 characters, no spaces or control characters, no user name or password and no port other than 80 or 443. Each refusal explains why.
- **Every outbound request,** and every redirect hop, resolves DNS and only reaches public addresses on ports 80 and 443, with at most 5 redirects and 400 KB per page. Malformed ports and embedded credentials are refused.
- **Scans are limited** per client and in total. The client is identified by the address Cloudflare saw (`CF-Connecting-IP`), so a forged `X-Forwarded-For` can't dodge the limit, and clients are forgotten once their window passes. Request bodies are capped at 16 KB.
- **Text from the internet is data,** fenced in prompts and escaped in reports, issues and pull requests. Links from scan results are rendered only when they are web addresses.
- **Patches are built on the server** from the saved autopsy, never from what the browser sends. The Action only opens a pull request and an issue, never merges, and only acts on its own repository.
- **Each autopsy can be preserved only once,** to respect the Internet Archive.
- **Every response** carries a strict Content Security Policy without inline scripts, HSTS, `nosniff`, `no-referrer`, a Permissions Policy and a Cross Origin Opener Policy. The container runs as an unprivileged user.
- **Secrets never live in the repository.** Locally they go in `backend/.env`, in production in the Render dashboard and for the Action in GitHub repository secrets.

See [SECURITY.md](SECURITY.md) to report a vulnerability.

## Accessibility and design

- Semantic HTML, a skip link, visible keyboard focus and `aria-live` regions for progress, waiting, copying and errors. Focus moves to the results when they arrive.
- The animations switch and `prefers-reduced-motion` stop the ghost, the petals, the house, the waiting ghost and the footer candle.
- No horizontal scroll down to 320 px, with the header and the results reorganized for phones.
- Body text in Atkinson Hyperlegible, designed for readers with low vision, and headings in IM Fell English, a 17th century print face that fits honoring the past.
- Serious, readable colors on a night background, with meaning carried by words as well as color.
- The footer is the edge of a graveyard, with headstones, an iron fence, a candle and an epitaph: "Here lie the links that led nowhere. May they rest, and may their pages be remembered."

![The graveyard footer with its epitaph, links and credits](docs/screenshots/footer-graveyard.png)

## Limits

- Linkmortem reads the HTML a server sends and doesn't run JavaScript, so sites built entirely with JavaScript (linkmortem.tech itself) are named as such. Their repository can be scanned instead.
- One scan checks up to 150 links, from up to 12 pages of a site or 40 Markdown files of a repository, and always says when it stopped early.
- The web is alive, so a link that timed out once may be unconfirmed in one scan and alive in the next.
- Search results depend on the daily budget, and links already resolved come from the cache or the graveyard for free.

## Run it locally

Backend, from the `backend` folder:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements_dev.txt
copy .env.example .env
ollama pull gemma4:e4b
ruff check .
python -m pytest
python -m uvicorn app.api:app
```

On macOS or Linux, use `source .venv/bin/activate` and `cp .env.example .env`.

Frontend, from the `frontend` folder:

```
npm ci
npm run format:check
npm test
npm run dev
```

Vite proxies `/api` to the backend at `http://localhost:8000`. Everything works with Ollama alone, and each key in `.env` turns on one more piece. [CONTRIBUTING.md](CONTRIBUTING.md) has the checks to run before a pull request and the project rules.

## Configuration

| Variable                                          | Default                     | What it does                                   |
| ------------------------------------------------- | --------------------------- | ---------------------------------------------- |
| `LINKMORTEM_MODEL_PROVIDER`                       | `ollama`                    | `ollama` or `backboard`                        |
| `LINKMORTEM_OLLAMA_MODEL`                         | `gemma4:e4b`                | Local model                                    |
| `OLLAMA_HOST`                                     | `http://localhost:11434`    | Ollama server                                  |
| `LINKMORTEM_NUM_CTX`                              | `8192`                      | Context window for Ollama                      |
| `BACKBOARD_API_KEY`                               | empty                       | Gemma through Backboard                        |
| `LINKMORTEM_BACKBOARD_PROVIDER`                   | `openrouter`                | Provider behind Backboard                      |
| `LINKMORTEM_BACKBOARD_MODEL`                      | `google/gemma-4-26b-a4b-it` | Model served by Backboard                      |
| `LINKMORTEM_MODEL_RETRIES`                        | `2`                         | Retries for an unusable model answer           |
| `MONGODB_URI`                                     | empty                       | Shared autopsies, caches and the graveyard     |
| `LINKMORTEM_DATABASE`                             | `linkmortem`                | Atlas database                                 |
| `SERPAPI_API_KEY`                                 | empty                       | Searching for new homes                        |
| `LINKMORTEM_MAX_SEARCHES`                         | `5`                         | Searches per scan                              |
| `LINKMORTEM_SEARCH_DAILY_BUDGET`                  | `20`                        | Searches per day for the whole server          |
| `ARCHIVE_ACCESS_KEY`, `ARCHIVE_SECRET_KEY`        | empty                       | Preserving living links with Save Page Now     |
| `SENTRY_DSN`                                      | empty                       | Agent traces                                   |
| `LINKMORTEM_ENVIRONMENT`                          | `development`               | Environment name in Sentry                     |
| `GITHUB_TOKEN`                                    | empty                       | 5,000 GitHub requests per hour instead of 60   |
| `LINKMORTEM_SCAN_CONCURRENCY`                     | `8`                         | Links checked at the same time                 |
| `LINKMORTEM_MODEL_CONCURRENCY`                    | `2`                         | Gemma calls at the same time                   |
| `LINKMORTEM_SCAN_LIMIT`, `LINKMORTEM_SCAN_WINDOW` | `5`, `600`                  | Scans per client per window, in seconds        |
| `LINKMORTEM_MAX_CONCURRENT_SCANS`                 | `2`                         | Scans running at the same time                 |
| `LINKMORTEM_TRUST_PROXY`                          | `false`                     | Read the client address from the proxy headers |
| `LINKMORTEM_CAPTURE_FILE`                         | empty                       | Records prompts for the evaluation             |
| `LINKMORTEM_PUBLIC_URL`                           | `https://linkmortem.tech`   | Address used in shared links and previews      |

## Deploy

`render.yaml` describes the service as a Render Blueprint: the Docker image (Node 24 builds the interface, Python 3.13 slim serves it as an unprivileged user), the health check at `/api/health`, deploys only after checks pass, the custom domain and every secret requested at creation instead of stored in the repository.

## Built with AI

Claude helped plan the work, write and review code, label the evaluation cases, debug and write the documentation. GitHub Copilot's coding agent wrote the first version of the security and contributing guides. Every change was reviewed, tested and committed by hand.

## Credits

Gemma's open weights by Google. The Wayback Machine, its CDX API and Save Page Now by the Internet Archive. Three.js for the ghost and the haunted house. IM Fell English, digitized by Igino Marini, and Atkinson Hyperlegible by the Braille Institute, both under the SIL Open Font License. Section anchors follow the way GitHub builds them from headings. The link rot figures on the home page come from Pew Research Center (2024) and Zittrain and colleagues (2021), as cited by the Internet Archive.

## License

[MIT](LICENSE)
