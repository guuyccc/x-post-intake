#!/usr/bin/env python3
"""抓取 X 帖子元数据（lark-doc x-post-intake skill 辅助脚本）。

用法: python3 tweet_meta.py <tweet_id>
输出: JSON {handle, name, text, likes, created_at, media_type, poster_url, duration_s, url}
依赖: 仅标准库 + 本机网络（cdn.syndication.twimg.com 公开接口）。
"""
import json
import sys
import urllib.request

def main():
    if len(sys.argv) < 2:
        print("usage: tweet_meta.py <tweet_id>", file=sys.stderr)
        sys.exit(1)
    tid = sys.argv[1].strip()
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tid}&token=x"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)

    user = d.get("user", {}) or {}
    media = d.get("mediaDetails") or []
    if not media and d.get("quoted_tweet"):
        media = (d.get("quoted_tweet") or {}).get("mediaDetails") or []

    media_type, poster, duration_s = None, None, None
    photos = []
    for m in media:
        t = m.get("type")
        if t == "video" and media_type != "video":
            media_type = "video"
            poster = m.get("media_url_https")
            duration_s = round((m.get("video_info", {}).get("duration_millis") or 0) / 1000, 1)
        elif t == "photo":
            photos.append(m.get("media_url_https"))
    if media_type != "video" and photos:
        media_type = "photo"
        poster = photos[0]

    out = {
        "tweet_id": tid,
        "url": f"https://x.com/{user.get('screen_name')}/status/{tid}",
        "handle": user.get("screen_name"),
        "name": user.get("name"),
        "text": d.get("text"),
        "likes": d.get("favorite_count"),
        "created_at": d.get("created_at"),
        "media_type": media_type,
        "poster_url": poster,
        "photos": photos,
        "duration_s": duration_s,
        "quoted": bool(d.get("quoted_tweet")),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
