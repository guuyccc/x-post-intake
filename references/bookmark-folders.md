# X 书签文件夹进入 SOP

书签文件夹（bookmark folder/collection）里的帖子**只能**通过书签页 UI 的下拉菜单进入。直接导航文件夹 URL（`https://x.com/i/history/bookmarks/<id>`）必现 "Something went wrong" 错误页——不要重试直接导航。

## 进入步骤（照此执行，勿改序）

1. **打开书签页**：webbridge `navigate` 到 `https://x.com/i/history`，等待 `article` 元素出现（约 6~9 秒）。
2. **展开文件夹下拉**：`snapshot` 找到 `role=tab`、name 为 `Bookmarks` 的元素（例：`@e23`），用 **webbridge 原生 `click` 动作**点击（`{"action":"click","args":{"selector":"@eXX"}}`）。
   - ⚠️ **禁止在 `evaluate` 里用 JS `.click()`**——下拉菜单状态跨调用存活不住，下一次 evaluate 时菜单已关闭。原生 click + 重新 snapshot 才可靠。
   - ⚠️ 不要点 h2 文本：主书签页 h2 是「Bookmarks」，但文件夹页的 h2 是文件夹名，点错对象。
3. **选择文件夹**：重新 `snapshot`，找到 `role=menuitemradio` 且 name 为目标文件夹名（如 `Case Sept`、`Sonnet 5.5`）的项，原生 `click`。
4. **自检**：确认 `location.href` 形如 `x.com/i/history/bookmarks/<id>` 且 `document.querySelectorAll("article").length > 0`。
   - 若页面显示 "Something went wrong" 或 articles=0 → 回到第 1 步重走 UI 路径，**不要**尝试直接刷新文件夹 URL。
5. **抓全量**：循环滚动（每次 `window.scrollBy(0, 2500)`，间隔 1.5s），收集每个 article 的 `/status/<id>` 链接、作者、时间、文本；**连续 4 轮无新增即视为到底**。

## 已知陷阱

- `/i/history/bookmarks/<id>` 中的 id 是**文件夹 id，不是 tweet_id**——对文件夹 id 调 `cdn.syndication.twimg.com/tweet-result` 会返回 HTML 错误页而不是 JSON。凡不含 `/status/` 的 URL 一律不当 tweet_id。
- 下拉项可能不止目标文件夹（All Bookmarks / 各文件夹 / Case Collection 👍 等），按 name 精确匹配，不要点序号。
- evaluate 之间页面会被 X 的 SPA 重渲染，元素引用（getBoundingClientRect、暂存变量）跨调用不可靠；每次都重新 snapshot 取最新 `@e` ref。
