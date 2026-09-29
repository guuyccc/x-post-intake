# X Post Intake

An installable AI-agent skill for turning an X (Twitter) post into a fully-formatted social-media research entry.

Given one post link (or a pick from the user's X bookmarks), the agent will:

- fetch the tweet's text, author, likes, and media via the public syndication API
- scrape the view count from the live post page with the user's logged-in browser
- attach the post's own cover image (no GIF pipelines — Feishu degrades them anyway)
- write a short Chinese title and a one-line summary quoting the author's own evaluation
- classify the post into a fixed 5-category / 9-sub-tag taxonomy with explicit boundary rules
- insert a formatted cell into a categorized "case wall" in a Feishu doc, sorted by likes (rebuilding the target table, preserving teammates' edits)
- hunt for a shared prompt or related link in the post and the author's replies (with an X-search fallback when the reply feed fails to load) and append it to the cell
- record everything in a Feishu Bitable with a strict, documented field schema
- deduplicate against both the doc and the Bitable before writing anything

## Install

Copy the complete `x-post-intake` folder into your agent application's skills directory (e.g. `~/.agents/skills/`). If the application has no native skill system, import the folder as project knowledge and use `SKILL.md` as the entry instruction.

See [INSTALL.md](INSTALL.md) for requirements, first-run setup, and a smoke test.

## First run

Before the first write, the agent must ask for and fill in the four project constants in `SKILL.md`:

1. the Feishu research doc (docx document id + the case-wall section's block id)
2. the Feishu Bitable (base-token + table-id)

Target links, tokens, credentials, and private organization settings must remain outside the shareable skill folder.

## Requirements

- Python 3 (standard library only)
- `curl`
- `lark-cli` with the `lark-doc` and `lark-base` skills (Feishu doc + Bitable writes)
- a logged-in-browser bridge such as `kimi-webbridge` (view counts, bookmarks, reply search)
- an X (Twitter) session in that browser

## Structure

```
x-post-intake/
├── SKILL.md                  # main workflow
├── references/
│   └── standards.md          # taxonomy, writing, and formatting standard (mirrors the live dataset)
└── scripts/
    └── tweet_meta.py         # tweet metadata fetcher (syndication API)
```

## Notes

- The classification taxonomy (5 categories / 9 sub-tags with boundary rules) lives in `references/standards.md` — adjust it there when the research framing changes.
- The Bitable field schema is documented in `SKILL.md` step 7; the skill re-reads the live schema before writing if it ever changes.
