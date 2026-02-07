---
description: Crawl documentation/wiki sites and save as local markdown files for on-demand reading.
argument-hint: <URL> [--depth N] [--max-pages N]
allowed-tools: Bash, Read, Glob
---

# Documentation Site Crawler

Crawl a documentation or wiki site and save content as local markdown files.

## User Input

$ARGUMENTS

## Setup Check

Before crawling, verify the tool is installed. Run:

```bash
test -f "${CLAUDE_PLUGIN_ROOT}/.venv/bin/crawl-docs" && echo "READY" || echo "NEEDS_SETUP"
```

If `NEEDS_SETUP`, run the following setup (only needed once):

```bash
python3 -m venv "${CLAUDE_PLUGIN_ROOT}/.venv" && "${CLAUDE_PLUGIN_ROOT}/.venv/bin/pip" install -e "${CLAUDE_PLUGIN_ROOT}" && "${CLAUDE_PLUGIN_ROOT}/.venv/bin/crawl4ai-setup"
```

This takes a few minutes (downloads browser engine). Inform the user that first-time setup is in progress.

## Determine Command

Parse the user's input from $ARGUMENTS:

- If a single URL with no extra flags → use `site` (default, most useful)
- If user explicitly says "single page" or "just this page" → use `page`
- `--depth N` and `--max-pages N` are optional, defaults are depth=3, max-pages=50

## Execute Crawl

### Crawl entire site (default)

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/crawl-docs" site "<URL>" --depth 3 --max-pages 50
```

### Crawl single page

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/crawl-docs" page "<URL>"
```

Crawling takes time (tens of seconds to minutes). This is normal — inform the user.

## Read Results

After crawl completes, the output is at `.crawl/<domain>/`.

### Step 1: Read the index

```
Read .crawl/<domain>/index.md
```

This shows all crawled pages with titles and file paths.

### Step 2: Read pages on-demand

Based on the user's question, read only the relevant page files. Do NOT read all pages at once.

### Step 3: Answer the user

Synthesize information from the pages you read. If more context is needed, read additional pages.

## Notes

- `.crawl/` directory is created in the current working directory
- Re-crawling the same domain overwrites previous results
- If crawl fails, check if the URL is correct and the site is accessible
- Some JS-heavy sites may need higher depth to capture all content
