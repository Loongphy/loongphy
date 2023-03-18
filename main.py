import feedparser
import pathlib
import datetime
import re


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(
        marker, chunk, marker)
    return r.sub(chunk, content)


def formatGMTime(timestamp):
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    dateStr = datetime.datetime.strptime(
        timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
    return dateStr.date()


def fetch_blog():
    '''解析博客'''
    items = feedparser.parse('https://blog.loongphy.com/rss.xml')['entries']
    return [
        {
            "title": item.title,
            "url": item.link,
            "published": formatGMTime(item.published)
        }
        for item in items
    ]


if __name__ == '__main__':
    root = pathlib.Path(__file__).parent.resolve()
    readme = root / "README.md"
    readme_contents = readme.open().read()

    entries = fetch_blog()[:5]
    entries_md = "\n".join(
        ["* <a href={url} target='_blank'>{title}</a> - {published}"
         .format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(readme_contents, "blog", entries_md)
    readme.open("w").write(rewritten)
