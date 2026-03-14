from __future__ import annotations

import html
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Post:
    title: str
    date_iso: str
    date_display: str
    url: str
    path: Path
    category: str | None
    tags: list[str]
    article_html: str
    toc_html: str
    excerpt: str
    word_count: int


def encode_url(parts: list[str]) -> str:
    return "/" + "/".join(quote(part) for part in parts) + "/"


def strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_first(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.I | re.S)
    return match.group(1).strip() if match else default


def extract_all_names(section: str, text: str) -> list[str]:
    names = re.findall(rf'href="/{section}/([^"/]+)/"', text)
    return [unquote(name) for name in names]


def parse_post(path: Path) -> Post:
    raw = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    year, month, day = rel.parts[0:3]
    title = path.parent.name
    article_html = extract_first(r"<article>([\s\S]*?)</article>", raw)
    toc_html = extract_first(r'(<ol class="toc">[\s\S]*?</ol>)', raw)
    stats_html = extract_first(r'<div id="post" class="dearmsdan-post-Statistics">([\s\S]*?)</div>', raw)
    categories = extract_all_names("categories", stats_html)
    tags = extract_all_names("tags", stats_html)
    clean_text = strip_html(article_html)
    excerpt = clean_text[:140] + ("..." if len(clean_text) > 140 else "")
    word_count = len(clean_text)
    date_iso = f"{year}-{month}-{day}"
    date_display = f"{year}.{month}.{day}"
    url = encode_url(list(rel.parts[:-1]))
    return Post(
        title=title,
        date_iso=date_iso,
        date_display=date_display,
        url=url,
        path=path,
        category=categories[0] if categories else None,
        tags=tags,
        article_html=article_html,
        toc_html=toc_html,
        excerpt=excerpt,
        word_count=word_count,
    )


def page_shell(title: str, description: str, body: str, extra_scripts: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="icon" href="/logo.jpg" type="image/jpeg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/home.css">
</head>
<body>
  <div class="site-shell">
    <div class="site-bg" aria-hidden="true">
      <div class="aurora aurora-one"></div>
      <div class="aurora aurora-two"></div>
      <div class="aurora aurora-three"></div>
      <div class="grid"></div>
      <div class="noise"></div>
    </div>
    <header class="site-header" id="top">
      <nav class="nav">
        <a class="brand" href="/">
          <span class="brand-mark">TX</span>
          <span class="brand-copy">
            <strong>TinloneX</strong>
            <small>Personal Tech Blog</small>
          </span>
        </a>
        <button class="nav-toggle" type="button" aria-label="切换导航" aria-expanded="false" aria-controls="site-menu">
          <span></span>
          <span></span>
        </button>
        <div class="nav-menu" id="site-menu">
          <a href="/">Home</a>
          <a href="/archives/">Archives</a>
          <a href="/tags/">Tags</a>
          <a href="/categories/">Categories</a>
          <a href="/about.html">About</a>
          <a href="/valine.html">留言板</a>
          <a href="https://github.com/TinloneX/" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </nav>
    </header>
    {body}
    <footer class="site-footer">
      <p>© 2026 TinloneX. Static pages restyled into a unified personal brand experience.</p>
      <div class="footer-links">
        <a href="/">Home</a>
        <a href="/archives/">Archives</a>
        <a href="/tags/">Tags</a>
        <a href="/categories/">Categories</a>
      </div>
    </footer>
  </div>
  <script src="/js/home.js"></script>
  {extra_scripts}
</body>
</html>
"""


def render_post_meta(post: Post) -> str:
    chips = [f'<span class="meta-chip">{post.date_display}</span>', f'<span class="meta-chip">{post.word_count} chars</span>']
    if post.category:
      chips.append(f'<a class="meta-chip" href="{category_url(post.category)}">{html.escape(post.category)}</a>')
    chips.extend(f'<a class="meta-chip" href="{tag_url(tag)}">{html.escape(tag)}</a>' for tag in post.tags)
    return "".join(chips)


def render_post_page(post: Post) -> str:
    toc_block = (
        f'<aside class="toc-panel reveal"><h2>目录</h2>{post.toc_html}</aside>'
        if post.toc_html
        else '<aside class="toc-panel reveal"><h2>目录</h2><p class="hero-text">这篇文章没有生成目录，直接向下阅读即可。</p></aside>'
    )
    body = f"""
    <main>
      <section class="section page-hero">
        <div class="section-heading reveal">
          <p class="eyebrow">ARTICLE</p>
          <h2>{html.escape(post.title)}</h2>
          <p class="hero-text">{html.escape(post.excerpt or "技术文章详情页")}</p>
          <div class="meta-row">{render_post_meta(post)}</div>
        </div>
      </section>
      <section class="section content-section">
        <div class="article-layout">
          <article class="article-shell reveal">
            <div class="article-main-header">
              <h1>{html.escape(post.title)}</h1>
              <div class="meta-row">{render_post_meta(post)}</div>
            </div>
            <div class="article-body prose">
              {post.article_html}
            </div>
          </article>
          {toc_block}
        </div>
      </section>
      <section class="section connect">
        <div class="comment-shell reveal">
          <div class="comment-shell-head">
            <p class="eyebrow">VALINE</p>
            <h2>继续讨论这篇文章</h2>
            <p>评论按当前文章路径独立保存，欢迎继续交流文章里的问题和想法。</p>
          </div>
          <div id="vcomments" class="comment-board"></div>
        </div>
      </section>
    </main>
    """
    scripts = """
  <script src="/js/valine.js"></script>
  <script>
    window.valine = new Valine({
      el: '#vcomments',
      appId: 'jNrzXxvqR3NhebnE7swyQBFp-gzGzoHsz',
      appKey: 'iqXsTlkThMqeaKdhYcgajztG',
      avatar: 'robohash',
      placeholder: '输入昵称、邮箱后，留下你想交流的内容吧。',
      path: window.location.pathname
    });
  </script>
"""
    return page_shell(f"{post.title} | TinloneX", post.excerpt or post.title, body, scripts)


def render_list_card(post: Post) -> str:
    tag_chips = "".join(f'<a class="meta-chip" href="{tag_url(tag)}">{html.escape(tag)}</a>' for tag in post.tags[:3])
    category_chip = f'<a class="meta-chip" href="{category_url(post.category)}">{html.escape(post.category)}</a>' if post.category else ""
    return f"""
      <a class="list-card reveal" href="{post.url}">
        <div class="list-card-head">
          <div>
            <h3>{html.escape(post.title)}</h3>
            <p>{html.escape(post.excerpt)}</p>
          </div>
          <span class="taxonomy-count">{post.date_iso}</span>
        </div>
        <div class="list-card-meta">
          {category_chip}
          {tag_chips}
        </div>
      </a>
"""


def category_url(name: str | None) -> str:
    return encode_url(["categories", name]) if name else "/categories/"


def tag_url(name: str) -> str:
    return encode_url(["tags", name])


def render_collection_page(title: str, eyebrow: str, description: str, cards: str) -> str:
    body = f"""
    <main>
      <section class="section page-hero">
        <div class="section-heading reveal">
          <p class="eyebrow">{html.escape(eyebrow)}</p>
          <h2>{html.escape(title)}</h2>
          <p class="hero-text">{html.escape(description)}</p>
        </div>
      </section>
      <section class="section content-section">
        <div class="list-grid">
          {cards if cards else '<div class="empty-state reveal">当前没有可展示的内容。</div>'}
        </div>
      </section>
    </main>
"""
    return page_shell(f"{title} | TinloneX", description, body)


def render_taxonomy_index(title: str, eyebrow: str, description: str, items: list[tuple[str, list[Post]]], url_builder) -> str:
    cards = []
    for name, posts in items:
        links = "".join(f'<li><a href="{post.url}">{html.escape(post.title)}</a></li>' for post in posts[:3])
        cards.append(f"""
        <a class="taxonomy-card reveal" href="{url_builder(name)}">
          <span class="taxonomy-count">{len(posts)} POSTS</span>
          <h3>{html.escape(name)}</h3>
          <p>{html.escape(posts[0].excerpt if posts else '')}</p>
          <ul class="mini-list">{links}</ul>
        </a>
        """)
    body = f"""
    <main>
      <section class="section page-hero">
        <div class="section-heading reveal">
          <p class="eyebrow">{html.escape(eyebrow)}</p>
          <h2>{html.escape(title)}</h2>
          <p class="hero-text">{html.escape(description)}</p>
        </div>
      </section>
      <section class="section content-section">
        <div class="taxonomy-grid">
          {''.join(cards) if cards else '<div class="empty-state reveal">当前没有可展示的内容。</div>'}
        </div>
      </section>
    </main>
"""
    return page_shell(f"{title} | TinloneX", description, body)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    post_paths = sorted(ROOT.glob("20[0-9][0-9]/*/*/*/index.html"))
    posts = [parse_post(path) for path in post_paths]
    posts.sort(key=lambda item: item.date_iso, reverse=True)

    for post in posts:
        write(post.path, render_post_page(post))

    archive_cards = "".join(render_list_card(post) for post in posts)
    write(
        ROOT / "archives" / "index.html",
        render_collection_page(
            "Archives",
            "ARCHIVE",
            "按时间浏览全部文章，快速回到你想看的写作阶段和主题轨迹。",
            archive_cards,
        ),
    )

    posts_by_year = defaultdict(list)
    posts_by_month = defaultdict(list)
    for post in posts:
        year, month, _ = post.date_iso.split("-")
        posts_by_year[year].append(post)
        posts_by_month[(year, month)].append(post)

    for year, year_posts in posts_by_year.items():
        write(
            ROOT / "archives" / year / "index.html",
            render_collection_page(
                f"{year} Archives",
                "YEAR",
                f"浏览 {year} 年发布的全部文章。",
                "".join(render_list_card(post) for post in year_posts),
            ),
        )

    for (year, month), month_posts in posts_by_month.items():
        write(
            ROOT / "archives" / year / month / "index.html",
            render_collection_page(
                f"{year}-{month} Archives",
                "MONTH",
                f"浏览 {year} 年 {month} 月发布的文章。",
                "".join(render_list_card(post) for post in month_posts),
            ),
        )

    tags_map: dict[str, list[Post]] = defaultdict(list)
    categories_map: dict[str, list[Post]] = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            tags_map[tag].append(post)
        if post.category:
            categories_map[post.category].append(post)

    sorted_tags = sorted(tags_map.items(), key=lambda item: (-len(item[1]), item[0].lower()))
    sorted_categories = sorted(categories_map.items(), key=lambda item: (-len(item[1]), item[0].lower()))

    write(
        ROOT / "tags" / "index.html",
        render_taxonomy_index(
            "Tags",
            "TOPICS",
            "从主题角度浏览文章，快速定位 WorkManager、Lifecycle、性能优化等内容。",
            sorted_tags,
            tag_url,
        ),
    )

    for tag, tag_posts in sorted_tags:
        write(
            ROOT / "tags" / tag / "index.html",
            render_collection_page(
                f"Tag · {tag}",
                "TAG",
                f"与 {tag} 相关的文章集合。",
                "".join(render_list_card(post) for post in tag_posts),
            ),
        )

    write(
        ROOT / "categories" / "index.html",
        render_taxonomy_index(
            "Categories",
            "CATEGORIES",
            "从分类维度浏览文章，查看 Framework、Jetpack、性能优化等主题板块。",
            sorted_categories,
            category_url,
        ),
    )

    for category, category_posts in sorted_categories:
        write(
            ROOT / "categories" / category / "index.html",
            render_collection_page(
                f"Category · {category}",
                "CATEGORY",
                f"与 {category} 分类相关的文章集合。",
                "".join(render_list_card(post) for post in category_posts),
            ),
        )


if __name__ == "__main__":
    main()
