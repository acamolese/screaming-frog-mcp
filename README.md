# Screaming Frog MCP Server

MCP server that exposes Screaming Frog SEO Spider crawl data as tool calls for any MCP-compatible AI assistant.

Built on top of the [screamingfrog](https://github.com/Amaculus/screaming-frog-api) Python library.

## Requirements

- Python 3.10+
- Java runtime (for `.dbseospider` files with Derby backend)
- Screaming Frog SEO Spider installed (optional, for `.seospider` conversion)

## Installation

```bash
git clone https://github.com/acamolese/screaming-frog-mcp.git
cd screaming-frog-mcp
pip install -e .
```

## Configuration

Add to your MCP client configuration (e.g. `.mcp.json`):

```json
{
  "mcpServers": {
    "screaming-frog-seo": {
      "type": "stdio",
      "command": "screaming-frog-mcp"
    }
  }
}
```

## Available tools

| Tool | Description |
|------|-------------|
| `load_crawl` | Load a crawl file |
| `crawl_summary` | Get crawl statistics |
| `get_pages` | Query pages with filters (status code, indexability, text search, section) |
| `get_links` | Query inbound/outbound links |
| `broken_links_report` | Broken links report |
| `title_meta_audit` | Title and meta description audit |
| `indexability_audit` | Non-indexable pages |
| `redirect_chains_report` | Redirect chains |
| `canonical_issues_report` | Canonical tag issues |
| `hreflang_issues_report` | Hreflang issues |
| `orphan_pages_report` | Orphan pages |
| `security_issues_report` | Security issues |
| `redirect_issues_report` | Redirect issues |
| `nofollow_inlinks_report` | Nofollow inbound links |
| `compare_crawls` | Compare two crawls |
| `query_tab` | Access any crawl tab |
| `list_tabs` | List available tabs |
| `list_crawls` | Discover available crawls on the machine |

## Slash command for automated analysis

A ready-made slash command is available that runs a full technical SEO audit in one step. Copy the command file to your commands directory:

```bash
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/analyze-crawl.md \
  https://raw.githubusercontent.com/acamolese/screaming-frog-mcp/main/commands/analyze-crawl.md
```

Then type `/analyze-crawl` in a new session. The command will ask for your crawl file and automatically run all audits, presenting a structured report.

## Supported formats

- `.dbseospider` (Derby, native DB-mode format)
- `.seospider` (Screaming Frog project, requires CLI installed)
- `.duckdb` (DuckDB cache)
- `.db` (SQLite legacy)
- CSV export directories

## License

MIT
