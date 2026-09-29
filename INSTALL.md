# Install

## Migration modes

### A. Native skill system (recommended)

Copy the complete `x-post-intake` folder into the destination application's documented skills directory, for example:

```bash
cp -r x-post-intake ~/.agents/skills/
```

Restart or reload the agent so it picks up the new skill.

### B. Project knowledge import

If the application has no native skill system, import the folder as project knowledge and point the agent at `SKILL.md` as the entry instruction. Keep the relative paths `references/standards.md` and `scripts/tweet_meta.py` intact — `SKILL.md` references them.

## Requirements

- Python 3 (standard library only)
- `curl` or an equivalent HTTP client
- internet access
- `lark-cli` authenticated as the user, with `lark-doc` and `lark-base` skills available
- a logged-in-browser bridge (e.g. `kimi-webbridge`) holding the user's X session

## First-run setup

On the first run the agent must ask for, and fill into the constants table in `SKILL.md`:

1. **Research doc** — the Feishu docx document id that hosts the case wall, plus the block id of the h2 section that parents it (fetch the doc outline to resolve it).
2. **Bitable** — the base-token and table-id of the tracking table.

The Bitable must contain the fields documented in `SKILL.md` step 7 (`标题 / 作者 / 分类 / 子类 / Likes / Views / 一句话概括 / 帖子链接 / 发布日期 / 来源 / 已进文档`). If it does not exist yet, create it with the same names and select options before the first write.

Keep real internal tokens out of the shared/public copy of this skill.

## Smoke test

1. `python3 scripts/tweet_meta.py 2104094723887501736` → should print JSON with `handle: konstantinsaifo`, a `poster_url`, and a `likes` count.
2. Ask the agent: "把这条帖子录进去 https://x.com/<any fresh post>" → the agent should dedupe, fetch metadata, write the cell and the record, and report back the placement.
3. Run the same command again → the agent must answer "already recorded" and skip.
