import datetime
import pathlib
import re

import feedparser


def replace_chunk(content, marker, chunk, inline=False):
    pattern = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return pattern.sub(chunk, content)


def format_gmt_time(timestamp):
    gmt_format = "%a, %d %b %Y %H:%M:%S GMT"
    date_str = datetime.datetime.strptime(timestamp, gmt_format) + datetime.timedelta(hours=8)
    return date_str.date()


def fetch_blog(limit=3):
    items = feedparser.parse("https://loongphy.com/rss.xml")["entries"][:limit]
    return [
        {
            "title": item.title,
            "url": item.link,
            "published": format_gmt_time(item.published),
        }
        for item in items
    ]


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme = root / "README.md"
    readme_contents = readme.read_text(encoding="utf-8")

    entries = fetch_blog()
    entries_md = "\n".join(
        ["* <a href={url} target='_blank'>{title}</a> - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(readme_contents, "blog", entries_md)
    readme.write_text(rewritten, encoding="utf-8")
