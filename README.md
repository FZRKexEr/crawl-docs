# crawl-docs

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that crawls documentation/wiki sites and saves content as local markdown files.

Unlike MCP-based approaches where all crawled content is returned through the transport layer (slow, token-heavy), this plugin saves results to local files and lets Claude read them on-demand — only loading what's relevant to your question.

Powered by [crawl4ai](https://github.com/unclecode/crawl4ai).

## Install

```bash
git clone https://github.com/FZRKexEr/crawl-docs.git ~/.claude/plugins/crawl-docs
```

First time you run `/crawl`, it will automatically set up a Python venv and install dependencies (including a headless Chromium browser). This takes a few minutes.

## Usage

```
/crawl https://opencode.ai/docs
```

That's it. Claude will crawl the site, then read and answer based on the content.

### Options

```
/crawl https://example.com/docs --depth 5 --max-pages 100
```

| Option | Default | Description |
|--------|---------|-------------|
| `--depth N` | 3 | Max link depth to follow (1-10) |
| `--max-pages N` | 50 | Max number of pages to crawl (1-500) |

### Single page mode

If you only need one page:

```
/crawl https://example.com/docs/api-reference (just this page)
```

## How it works

1. `/crawl <url>` triggers a BFS deep crawl using a headless browser
2. Each page is saved as a separate `.md` file under `.crawl/<domain>/`
3. An `index.md` is generated listing all crawled pages
4. Claude reads the index, then selectively reads only the pages relevant to your question

```
.crawl/opencode.ai/
├── index.md
└── pages/
    ├── 000_docs.md
    ├── 001_docs_getting-started.md
    ├── 002_docs_configuration.md
    └── ...
```

## License

MIT
