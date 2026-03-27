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
pipx install -e .
```

Or with pip in a virtual environment:

```bash
pip install -e .
```

After installation, find the full path to the command:

```bash
which screaming-frog-mcp
```

You will need this path for the configuration below (typically `~/.local/bin/screaming-frog-mcp` when installed via pipx).

## Configuration

The MCP server needs to be registered in the config file of your MCP client. The file location and format vary depending on the client you use.

### Claude Code (CLI)

Add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "screaming-frog-seo": {
      "type": "stdio",
      "command": "/full/path/to/screaming-frog-mcp"
    }
  }
}
```

### Claude Desktop (macOS app)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`, inside the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "screaming-frog-seo": {
      "command": "/full/path/to/screaming-frog-mcp"
    }
  }
}
```

Note: Claude Desktop does not use the `"type": "stdio"` field. If the file already contains other MCP servers, just add the `"screaming-frog-seo"` entry alongside them.

### Other MCP clients

Refer to your client's documentation. The server uses stdio transport and the command is the path to `screaming-frog-mcp`.

**Important**: Always use the absolute path to the command (from `which screaming-frog-mcp`) rather than just the name, to avoid PATH resolution issues.

After editing the config, restart the application or session for changes to take effect.

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
