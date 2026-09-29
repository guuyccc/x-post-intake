---
name: x-post-intake
description: Turn an X (Twitter) post into a fully-formatted research entry — fetch content and metrics, write a title and one-line summary, classify into a fixed taxonomy, insert into a categorized "case wall" in a Feishu/Lark doc (sorted by likes), and record it in a Feishu Bitable. Use when the user says "record this X post", "add this post to the table", "process my X bookmarks", or pastes an x.com/twitter.com status link for intake.
---

# X Post Intake (social case research)

Turn one X post into a cell in a categorized case wall inside a Feishu doc + one record in a Feishu Bitable, with consistent formatting, metrics, and classification.

## Prerequisites

- Skills available: `lark-doc` (Feishu docs), `lark-base` (Feishu Bitable), `kimi-webbridge` or an equivalent logged-in-browser bridge (scraping view counts and the user's bookmarks).
- Read each skill's reference docs before calling their commands.

## Project constants (fill in on first run)

The skill needs four target identifiers. **On first run, ask the user for the Feishu doc and Bitable links, resolve the IDs below, and write them into this table before proceeding.** Keep real internal tokens out of the shared/public copy of this skill.

| Item | Value |
|---|---|
| Research doc doc_id | `<DOCX_DOCUMENT_ID>` (the `/docx/` id, resolvable from a `/wiki/` link) |
| Case-wall section block id | `<SECTION_H2_BLOCK_ID>` (the h2 heading that parents the wall) |
| Bitable base-token | `<BASE_TOKEN>` |
| Bitable table-id | `<TABLE_ID>` (starts with `tbl`) |

### Target-table routing

| Post content / folder name | Target Bitable | Insert into doc case wall? |
|---|---|---|
| Default (Opus 5.5 related) | main table (`<TABLE_ID>`) | yes |
| Sonnet 5.5 related / "Sonnet 5.5" folder | secondary table (same base, e.g. `<SONNET_TABLE_ID>`) | no — 「已进文档」 = `未进文档` |

> Add one row here for each new model-tracking table; set 「已进文档」 according to whether the wall insertion actually happened.

## Workflow

### Step 0: Input triage (three branches) + first-run name question

**On first use, ask the user: 「你叫什么名字？」** — the answer becomes the default 「来源」 value for every record written (e.g. `yicheng`); when recording on someone else's behalf, use that person's name. Then branch by input shape:

| User provides | Detection rule | Flow |
|---|---|---|
| `https://x.com/<handle>/status/<tweet_id>` | URL contains `/status/` | **Single-post flow**: extract tweet id → step 1 |
| Bookmark folder name (e.g. "Case Sept") or `x.com/i/history/bookmarks/<id>` or any `bookmarks` path | no `/status/` | **Folder batch flow**: enter the folder via the SOP in [`references/bookmark-folders.md`](references/bookmark-folders.md) → run step 1 per post |
| Just "my bookmarks" | nothing specific | open `x.com/i/history`, list the folders (menuitemradio items in the dropdown) + the 10 most recent bookmarks, let the user pick |

**Hard rules:**
- A URL without `/status/` is **never a tweet id** — no syndication call, no post fetch.
- **Never navigate directly** to a folder URL (`/i/history/bookmarks/<id>`) — X always returns "Something went wrong"; entry is only via the bookmarks-page dropdown.
- Folder batch flow: after scraping the full list, do a **scope confirmation** — tell the user "「{folder}」共 N 帖：{title list}，是否全部处理？"; for N≤5 a brief list then proceed is fine, for N>5 wait for explicit confirmation.
- Routing: if the folder name matches the routing table (e.g. "Sonnet 5.5") → the whole batch goes to that table; otherwise judge per post by content (Sonnet-5.5-mentioning posts → Sonnet table, everything else → default table).

### Step 1: Deduplicate (skip and name the duplicate)

1. Bitable: `lark-cli base +record-search --as user --base-token <BASE_TOKEN> --table-id <TABLE_ID> --json '{"keyword":"<tweet_id>","search_fields":["帖子链接"],"select_fields":["标题","分类","子类"],"limit":5}'`
2. Doc: `lark-cli docs +fetch --api-version v2 --doc <DOCX_DOCUMENT_ID> --scope keyword --keyword "<tweet_id>"`

If either hits, **tell the user exactly which existing entry it duplicates**: 「该帖已收录，与《{标题}》（{分类}/{子类}）重复，跳过。」(Use the returned Bitable fields when the table hits; use the cell's bold title from the doc when only the doc hits.) Never just say "duplicate" without naming it. In batch runs, name-and-skip each duplicate and keep processing the rest.

### Step 2: Fetch tweet metadata

```bash
python3 scripts/tweet_meta.py <tweet_id>
```

Returns JSON: `handle / name / text / likes / created_at / media_type / poster_url / duration_s / url` (media inside `quoted_tweet` is handled; `likes` = the post's own `favorite_count`).

### Step 3: Scrape Views

The syndication API has no view count — open the post in the logged-in browser:

1. `navigate` to the post URL, wait ~6s.
2. `evaluate`:
```js
const a=[...document.querySelectorAll("a")].find(x=>x.href.includes("/analytics"));
a ? a.textContent.replace(" Views","") : null
```
3. Record the X-native format verbatim (`1.5M`, `690.5K`, `5,850`) — **do not convert**.
4. If unavailable → write `待补` and note it in the final report.

### Step 4: Cover image

**Do not download videos or make GIFs** (Feishu degrades GIFs in heavy docs to static previews). Use the post's own cover:

- Video post: `poster_url` (the `media_url_https` amplify_video_thumb).
- Photo post: the photo itself.
- Download it locally, then upload into the doc to get a token:
```bash
lark-cli docs +media-insert --doc <DOCX_DOCUMENT_ID> --file <cover_file>
```
Returns `file_token` + a temp `block_id` appended at doc end (delete it in step 6).
- Note: `<img href="URL">` does NOT work for pbs.twimg.com (Feishu's server-side fetch is blocked) — you must download and upload.

### Step 5: Title, summary, classification, prompt links

Follow [`references/standards.md`](references/standards.md) exactly. Four outputs:

1. **Title**: 4–14 char Chinese label saying what the case does.
2. **One-line summary**: what it does + the author's own evaluation quoted in「」.
3. **Classification**: one of the 5 categories + one sub-tag (boundary rules in standards.md).
4. **Prompt / related links**: scan the post text AND the author's own replies for a shared prompt or related link (prompt doc, playable link, tool/Skill link; if the prompt only exists as a reply tweet, link that reply). Append at the very end of the cell: `<p>🔗 <a href="{url}">Prompt</a></p>` or `<p>🔗 <a href="{url}">相关链接</a></p>` (one per line).

> **⚠️ Reply-feed pitfall**: X post pages often fail to load replies (only the main article renders). Fallback: X search `https://x.com/search?q=from%3A<handle>%20<keyword>&f=live` (keyword: prompt / skill / link / 提示词), and find the author's "Replying to @self" tweet around the same date containing the prompt or link. Resolve `t.co` shortlinks with `curl -sIL -o /dev/null -w '%{url_effective}'`.

### Step 6: Insert into the case wall (likes-desc order)

Wall structure: h3 category → h4 sub-tag → 3-column `<table>`, cells sorted by Likes descending. **Feishu cannot add rows/cells to an existing table — you must rebuild the target table:**

1. `docs +fetch --api-version v2 --doc <DOCX_DOCUMENT_ID> --scope section --start-block-id <SECTION_H2_BLOCK_ID> --detail with-ids`; find the `<table>` right after the target h4 (sub-tag name).
2. Parse every `<td>`: keep its full inner XML (strip ` id="..."` attrs), parse likes from `❤️ ... Likes`.
3. Insert the new cell (template in standards.md) at the likes-desc position, rebuild the whole `<table>` (`<colgroup><col width="290"/>×3`).
4. `block_insert_after` the new table after the old one, then `block_delete` the old one.
5. **⚠️ If a cell contains a `<figure>` (e.g. an mp4 attachment card)**: strip the figure from the XML before rebuild, and before deleting the old table use `block_move_after` to move the figure into the matching cell of the new table (anchor = the cell's last `<p>` block id).
6. If the sub-tag group has no table yet (e.g. an empty "（待补充）" group): insert the new table right after that h4, and remove the「（待补充）」marker from the h4 text.
7. Delete the temp upload block from step 4.

### Step 7: Write the Bitable record

Bitable fields — write exactly these, names are case-sensitive:

| Field | Type | Rule |
|---|---|---|
| 标题 | text | from step 5 |
| 作者 | text | `@handle` |
| 分类 | select | 代码动画 / 动效动画 / 3D 场景与交互 / 三方软件接入 / 真实世界交互 (strict, never add options) |
| 子类 | select | 叙事短片 / 风格实验 / 产品宣发 / 游戏 / 场景 / 仿真 / 其他 / 真实建模 / 物理操控 (strict) |
| Likes | number | integer |
| Views | text | X-native value; `待补` if missing |
| 一句话概括 | text | from step 5 |
| 帖子链接 | text(url) | `https://x.com/<handle>/status/<tweet_id>` |
| 发布日期 | datetime | tweet `created_at` → ms epoch |
| 来源 | select | **contributor's name** (e.g. `yicheng`). On first use, ask the user "你叫什么名字？" and default to their answer; when recording on someone else's behalf, use that person's name. Legacy values: `初始调研`, `X 收藏夹` (do not write these anymore) |
| 已进文档 | select | `已进文档` (wall insertion done) / `未进文档` (recorded only) |

```bash
lark-cli base +record-upsert --as user --base-token <BASE_TOKEN> --table-id <TABLE_ID> \
  --json '{"标题":"...","作者":"@handle","分类":"...","子类":"...","Likes":1234,"Views":"...","一句话概括":"...","帖子链接":"https://x.com/handle/status/<tweet_id>","发布日期":<ms_epoch>,"来源":"X 收藏夹","已进文档":"已进文档"}'
```

> If the schema ever changes, run `lark-cli base +field-list --as user --base-token <BASE_TOKEN> --table-id <TABLE_ID>` first and update this file to match.

### Step 8: Report

Tell the user: title, category/sub-tag, Likes/Views, position within the group, links to the doc and the Bitable, plus the classification rationale (especially for boundary cases).

## Maintenance: the 「是否重复」 column (self-computing formula field)

The table has a **formula field** 「是否重复」 with expression:

```
IF([Opus 5.5].COUNTIF(CurrentValue.[帖子链接] = [帖子链接]) >= 2, "重复", "")
```

- How it works: `[TableName].COUNTIF(...)` takes the whole table as data range; `CurrentValue.[帖子链接]` is the iterated row's link, `[帖子链接]` is the formula row's link. Count ≥ 2 → shows 「重复」. It auto-marks new duplicates and auto-clears when a duplicate is removed — no recomputation needed.
- **⚠️ The expression references the table by NAME (currently `Opus 5.5`; the table-id `<TABLE_ID>` is stable). If the table gets renamed, the formula breaks and must be rewritten with the new name.**
- Writing a formula field: `lark-cli base +field-update --json '{"type":"formula","name":"是否重复","expression":"..."}' --yes --i-have-read-guide` (formula type requires `--i-have-read-guide`).

## Hard rules

- **Order**: dedupe first; gather all data before writing; rebuild the new table before deleting the old one.
- **Sorting**: strictly Likes descending within each group, left-to-right, top-to-bottom.
- **Images**: static covers only — no GIFs, no video blocks (not supported by the API).
- **Others' content**: teammates may add screenshots, localized stats lines, attachment cards to cells — preserve cell XML verbatim when rebuilding tables.
- **Concurrency**: run all lark-cli writes sequentially, never in parallel.
