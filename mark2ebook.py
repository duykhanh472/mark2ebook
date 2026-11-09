#!/usr/bin/env python3
"""
mark2epub: Convert Markdown files to high-quality EPUB 3 ebooks
matching the standard and typography of Standard Ebooks (standardebooks.org).
Requires a directory with 'book.yml' and a 'src/' content folder.
"""

import argparse
import html
import html.entities
import mimetypes
import os
import re
import sys
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import markdown
import yaml
from bs4 import BeautifulSoup
from pygments.formatters import HtmlFormatter

# ==============================================================================
# Standard Ebooks Built-in Stylesheets
# ==============================================================================

CORE_CSS = """@charset "utf-8";
@namespace epub "http://www.idpf.org/2007/ops";

body{
	font-variant-numeric: oldstyle-nums;
	hyphens: auto;
	adobe-hyphenate: auto;
	-webkit-hyphens: auto;
	-moz-hyphens: auto;
	text-wrap: pretty;
}

p{
	margin-top: 0;
	margin-right: 0;
	margin-bottom: 0;
	margin-left: 0;
	text-indent: 1em;
}

hr{
	border: none;
	border-top: 1px solid;
	height: 0;
	margin-top: 1.5em;
	margin-right: auto;
	margin-bottom: 1.5em;
	margin-left: auto;
	width: 25%;
}

q::before,
q::after{
	content: "";
}

blockquote{
	margin-top: 1em;
	margin-right: 2.5em;
	margin-bottom: 1em;
	margin-left: 2.5em;
}

h1,
h2,
h3,
h4,
h5,
h6,
hgroup{
	break-after: avoid;	
	page-break-after: avoid;
	break-inside: avoid;	
	page-break-inside: avoid;
	font-variant: small-caps;
	hyphens: none;
	adobe-text-layout: optimizeSpeed;
	adobe-hyphenate: none;
	-webkit-hyphens: none;
	-moz-hyphens: none;
	margin-top: 3em;
	margin-right: 0;
	margin-bottom: 3em;
	margin-left: 0;
	text-align: center;
}

hgroup.has-h1{
	margin-top: 6em;
	margin-right: 0;
	margin-bottom: 6em;
	margin-left: 0;
}

hgroup.has-h2{
	margin-top: 4.5em;
	margin-right: 0;
	margin-bottom: 4.5em;
	margin-left: 0;
}

hgroup.has-h3{
	margin-top: 3.51em;
	margin-right: 0;
	margin-bottom: 3.51em;
	margin-left: 0;
}

hgroup.has-h4{
	margin-top: 3em;
	margin-right: 0;
	margin-bottom: 3em;
	margin-left: 0;
}

hgroup.has-h5{
	margin-top: 2.49em;
	margin-right: 0;
	margin-bottom: 2.49em;
	margin-left: 0;
}

hgroup.has-h6{
	margin-top: 2.01em;
	margin-right: 0;
	margin-bottom: 2.01em;
	margin-left: 0;
}

hgroup > *{
	margin-top: 0;
	margin-right: 0;
	margin-bottom: 0;
	margin-left: 0;
}

hgroup > h1 + p{
	font-size: 1.5em;
}

hgroup > h2 + p{
	font-size: 1.17em;
}

hgroup > h2 + p + p,
hgroup > h3 + p{
	font-size: 1em;
}

hgroup > h2 + p + p + p,
hgroup > h3 + p + p,
hgroup > h4 + p{
	font-size: .83em;
}

hgroup > h2 + p + p + p + p,
hgroup > h3 + p + p + p,
hgroup > h4 + p + p,
hgroup > h5 + p{
	font-size: .67em;
}

hgroup > p.first-child{
	font-weight: bold;
}

hgroup > p{
	text-indent: 0;
}

p.continued,
h1 + p,
h2 + p,
h3 + p,
h4 + p,
h5 + p,
h6 + p,
header + p,
hr + p,
hgroup + p,
p.first-child{
	hanging-punctuation: first last;
	text-indent: 0;
}

cite{
	font-style: normal;
}

abbr{
	border: none;
	white-space: nowrap;
}

blockquote cite{
	display: block;
	font-style: italic;
	text-align: right;
}

blockquote cite i{
	font-style: normal;
}

b,
strong{
	font-variant: small-caps;
	font-weight: normal;
}

i > i,
em > i,
i > em{
	font-style: normal;
}

ol,
ul{
	margin-bottom: 1em;
	margin-top: 1em;
}

header{
	break-after: avoid;	
	page-break-after: avoid;
	break-inside: avoid;	
	page-break-inside: avoid;
	hyphens: none;
	adobe-text-layout: optimizeSpeed;
	adobe-hyphenate: none;
	-webkit-hyphens: none;
	-moz-hyphens: none;
	text-align: center;
}

header > * + p{
	text-indent: 0;
}

article > header + *,
section > header + *{
	margin-top: 3em;
}

a.epub-type-contains-word-noteref{
	font-size: smaller;
	font-style: normal !important;
	vertical-align: super;
}

section.epub-type-contains-word-endnotes > ol > li{
	margin-top: 1em;
	margin-right: 0;
	margin-bottom: 1em;
	margin-left: 0;
}

table{
	border-collapse: collapse;
	margin-top: 2em;
	margin-bottom: 2em;
	margin-left: auto;
	margin-right: auto;
	width: 90%;
}

th, td{
	border: 1px solid #ccc;
	padding: 0.5em 0.8em;
	text-align: left;
}

th{
	background-color: #f2f2f2;
	font-variant: small-caps;
}

@media all and (prefers-color-scheme: dark){
	img.epub-type-contains-word-se-image-color-depth-black-on-transparent{
		filter: invert(100%);
	}

	img.epub-type-contains-word-se-image-color-depth-black-on-transparent.epub-type-contains-word-se-image-style-realistic{
		background: currentColor;
		filter: none;
	}
}

article,
aside,
figure,
figcaption,
footer,
header,
main,
nav,
section{
	display: block;
}

section.epub-type-contains-word-titlepage h1,
section.epub-type-contains-word-titlepage p{
	display: none;
}

@supports(font-size: 0){
	section.epub-type-contains-word-titlepage h1,
	section.epub-type-contains-word-titlepage p{
		display: block;
	}
}

img.epub-type-contains-word-se-image-color-depth-black-on-transparent{
	background: #fff !important;
}

.epub-type-contains-word-titlepage img.epub-type-contains-word-se-image-color-depth-black-on-transparent{
	background: transparent !important;
}

@media all and (prefers-color-scheme){
	img.epub-type-contains-word-se-image-color-depth-black-on-transparent:not(.epub-type-contains-word-se-image-style-realistic){
		background: transparent !important;
	}
}

img{
	max-width: 100%;
	height: auto;
}
"""

SE_CSS = """@charset "utf-8";
@namespace epub "http://www.idpf.org/2007/ops";

section.epub-type-contains-word-titlepage{
	text-align: center;
	margin-top: 2em;
}

section.epub-type-contains-word-titlepage h1{
	font-size: 2em;
	margin-bottom: 0.5em;
}

section.epub-type-contains-word-titlepage p{
	font-size: 1.2em;
	margin-top: 0;
	margin-bottom: 2em;
	text-indent: 0;
}

section.epub-type-contains-word-titlepage img{
	display: block;
	margin-top: 2em;
	margin-right: auto;
	margin-bottom: auto;
	margin-left: auto;
	max-width: 90%;
	height: auto;
}
"""

# ==============================================================================
# Data Structures & Sorting
# ==============================================================================

def natural_sort_key(s: str | Path) -> list:
    """
    Sort key for natural alphanumeric ordering (e.g., '1. Intro', '2. Cat' ... '10. Move').
    """
    name = s.name if isinstance(s, Path) else str(s)
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", name)]


@dataclass
class Chapter:
    id_name: str
    title: str
    source_file: Path
    output_filename: str
    has_heading_in_source: bool = False
    content_html: str = ""


@dataclass
class BookMetadata:
    title: str = "Untitled Book"
    author: str = "Anonymous"
    description: str = ""
    language: str = "en"
    publisher: str = "Standard Ebooks"
    rights: str = "Public Domain"
    uid: str = field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    pub_date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    modified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    cover_image: Optional[Path] = None
    create_titlepage: bool = False
    chapters: List[Chapter] = field(default_factory=list)
    images: List[Path] = field(default_factory=list)
    custom_css: List[Path] = field(default_factory=list)

# ==============================================================================
# Helper Functions: Typography & XHTML Cleaning
# ==============================================================================

def decode_html_typography(text: str) -> str:
    """
    Decodes HTML entities to literal UTF-8 unicode (curly quotes, dashes, ellipses)
    while preserving XML-mandatory escaped characters (&lt;, &gt;, &amp;, &apos;, &quot;).
    """
    xml_entities = {"lt", "gt", "amp", "apos", "quot"}

    def replace_entity(match: re.Match) -> str:
        entity = match.group(1)
        if entity in xml_entities:
            return match.group(0)

        # Numerical hexadecimal &#x2014;
        if entity.startswith("#x") or entity.startswith("#X"):
            try:
                cp = int(entity[2:], 16)
                if cp in (60, 62, 38, 39, 34):
                    return match.group(0)
                return chr(cp)
            except ValueError:
                return match.group(0)

        # Numerical decimal &#8212;
        if entity.startswith("#"):
            try:
                cp = int(entity[1:])
                if cp in (60, 62, 38, 39, 34):
                    return match.group(0)
                return chr(cp)
            except ValueError:
                return match.group(0)

        # Named entity &mdash;
        if entity in html.entities.name2codepoint:
            return chr(html.entities.name2codepoint[entity])

        return match.group(0)

    return re.sub(r"&([#a-zA-Z0-9]+);", replace_entity, text)


def clean_and_format_xhtml(html_text: str, chapter_title: str, has_heading_in_source: bool = True) -> str:
    """
    Cleans markdown HTML, ensures valid self-closing tags (<img/>, <hr/>, <br/>),
    rewrites image paths to standard ../images/, and ensures heading structure.
    """
    html_text = decode_html_typography(html_text)
    soup = BeautifulSoup(html_text, "html.parser")

    # If the markdown source does not have a top-level heading (# Heading),
    # insert a clean semantic chapter header at the top
    if not has_heading_in_source and chapter_title:
        header_tag = soup.new_tag("header")
        h2_tag = soup.new_tag("h2")
        h2_tag["epub:type"] = "title"
        h2_tag.string = chapter_title
        header_tag.append(h2_tag)
        soup.insert(0, header_tag)

    # Rewrite image src and ensure alt attribute
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src.startswith("http://") and not src.startswith("https://") and not src.startswith("../"):
            if src.startswith("./"):
                src = src[2:]
            if src.startswith("images/"):
                img["src"] = "../" + src
            else:
                img["src"] = "../images/" + os.path.basename(src)
        if not img.get("alt"):
            img["alt"] = ""

    # Ensure self-closing XML tags using minimal formatter
    cleaned_body = soup.encode(formatter="minimal").decode("utf-8")
    return cleaned_body

# ==============================================================================
# Configuration & Content Loader (book.yml & src/ required)
# ==============================================================================

def load_book_config(book_dir: Path, force_titlepage: bool = False) -> BookMetadata:
    """
    Loads book.yml and processes chapters/assets located inside the required 'src/' subdirectory.
    """
    config_path = book_dir / "book.yml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing required 'book.yml' in directory: '{book_dir}'")

    src_dir = book_dir / "src"
    if not src_dir.is_dir():
        raise FileNotFoundError(f"Missing required 'src/' directory in: '{book_dir}'")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    folder_title = book_dir.name.replace("-", " ").replace("_", " ").title()
    title = str(config.get("title", folder_title)).strip() or folder_title
    author = str(config.get("author", "Anonymous")).strip() or "Anonymous"

    metadata = BookMetadata(
        title=title,
        author=author,
        description=str(config.get("description", "")).strip(),
        language=str(config.get("language", "en")).strip() or "en",
        publisher=str(config.get("publisher", "Standard Ebooks")).strip() or "Standard Ebooks",
        rights=str(config.get("rights", "Public Domain")).strip() or "Public Domain",
        create_titlepage=force_titlepage or bool(config.get("titlepage", False)),
    )

    # Resolve chapters: must reside inside src/
    raw_chapters = config.get("chapters", [])
    chapter_list: List[Tuple[str, str]] = []  # (title, filename)

    if raw_chapters:
        for idx, item in enumerate(raw_chapters):
            if isinstance(item, dict):
                if "title" in item and "file" in item:
                    chapter_list.append((str(item["title"]), str(item["file"])))
                else:
                    for k, v in item.items():
                        chapter_list.append((str(k), str(v)))
            elif isinstance(item, str):
                chapter_list.append(("", item))
    else:
        # If chapters list is omitted or empty in book.yml, scan all .md files in src/ with natural sorting
        md_files = list(src_dir.glob("*.md"))
        seen = set()
        unique_md = []
        for p in sorted(md_files, key=natural_sort_key):
            if p.name not in seen:
                seen.add(p.name)
                unique_md.append(p)
        for p in unique_md:
            chapter_list.append(("", p.name))

    for idx, (specified_title, filename) in enumerate(chapter_list):
        chapter_file = src_dir / filename
        if not chapter_file.is_file():
            raise FileNotFoundError(
                f"Chapter file '{filename}' listed in book.yml not found in '{src_dir}'"
            )

        # Check if source markdown has a top-level heading
        has_heading = False
        heading_title = None
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        has_heading = True
                        heading_title = stripped.lstrip("#").strip()
                        break
        except Exception:
            pass

        if specified_title:
            ch_title = specified_title
        elif heading_title:
            ch_title = heading_title
        else:
            ch_title = chapter_file.stem

        metadata.chapters.append(
            Chapter(
                id_name=f"chapter-{idx + 1}",
                title=ch_title,
                source_file=chapter_file,
                output_filename=f"chapter-{idx + 1}.xhtml",
                has_heading_in_source=has_heading,
            )
        )

    # Locate images in src/images/ or src/
    image_dirs = []
    img_cand = src_dir / "images"
    if img_cand.is_dir():
        image_dirs.append(img_cand)
    image_dirs.append(src_dir)

    found_images = {}
    for idir in image_dirs:
        for img_file in idir.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif"}:
                found_images[img_file.name] = img_file
    metadata.images = list(found_images.values())

    # Locate cover image in src/
    cover_conf = config.get("cover") or config.get("cover_image")
    if cover_conf:
        cand = src_dir / cover_conf
        if cand.is_file():
            metadata.cover_image = cand
        else:
            cand_img = src_dir / "images" / os.path.basename(cover_conf)
            if cand_img.is_file():
                metadata.cover_image = cand_img
    else:
        # Auto-detect cover image in found_images
        for name in ["cover.jpg", "cover.jpeg", "cover.png", "cover.webp"]:
            if name in found_images:
                metadata.cover_image = found_images[name]
                break

    if metadata.cover_image and metadata.cover_image not in metadata.images:
        metadata.images.append(metadata.cover_image)

    # Locate custom CSS in src/css/
    css_dir = src_dir / "css"
    if css_dir.is_dir():
        for cf in css_dir.glob("*.css"):
            if cf.is_file():
                metadata.custom_css.append(cf)

    return metadata

# ==============================================================================
# EPUB 3 File Generators
# ==============================================================================

def get_container_xml() -> str:
    return """<?xml version="1.0" encoding="utf-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
	<rootfiles>
		<rootfile full-path="epub/content.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>"""


def get_titlepage_xhtml(metadata: BookMetadata) -> str:
    cover_img_tag = ""
    if metadata.cover_image:
        cover_name = metadata.cover_image.name
        cover_img_tag = f"""\t\t\t<img alt="{html.escape(metadata.title)}" class="epub-type-contains-word-se-image-color-depth-black-on-transparent" src="../images/{cover_name}"/>\n"""

    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{metadata.language}" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="{metadata.language}">
	<head>
		<title>Titlepage</title>
		<link href="../css/core.css" rel="stylesheet" type="text/css"/>
		<link href="../css/se.css" rel="stylesheet" type="text/css"/>
	</head>
	<body epub:type="frontmatter">
		<section class="epub-type-contains-word-titlepage" id="titlepage" epub:type="titlepage">
			<h1 epub:type="title">{html.escape(metadata.title)}</h1>
			<p>By <b epub:type="z3998:author z3998:personal-name">{html.escape(metadata.author)}</b>.</p>
{cover_img_tag}\t\t</section>
	</body>
</html>"""


def get_chapter_xhtml(metadata: BookMetadata, chapter: Chapter) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{metadata.language}" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="{metadata.language}">
	<head>
		<title>{html.escape(chapter.title)}</title>
		<link href="../css/core.css" rel="stylesheet" type="text/css"/>
		<link href="../css/se.css" rel="stylesheet" type="text/css"/>
		<link href="../css/local.css" rel="stylesheet" type="text/css"/>
	</head>
	<body epub:type="bodymatter">
		<section id="{chapter.id_name}" role="doc-chapter" epub:type="chapter">
{chapter.content_html}
		</section>
	</body>
</html>"""


def get_toc_xhtml(metadata: BookMetadata) -> str:
    first_chapter_file = metadata.chapters[0].output_filename if metadata.chapters else "chapter-1.xhtml"
    
    toc_items = []
    if metadata.create_titlepage:
        toc_items.append('\t\t\t\t<li>\n\t\t\t\t\t<a href="text/titlepage.xhtml">Titlepage</a>\n\t\t\t\t</li>')

    for ch in metadata.chapters:
        toc_items.append(
            f"""\t\t\t\t<li>\n\t\t\t\t\t<a href="text/{ch.output_filename}">{html.escape(ch.title)}</a>\n\t\t\t\t</li>"""
        )
    chapter_items_str = "\n".join(toc_items)

    landmark_items = []
    if metadata.create_titlepage:
        landmark_items.append('\t\t\t\t<li>\n\t\t\t\t\t<a href="text/titlepage.xhtml" epub:type="frontmatter">Frontmatter</a>\n\t\t\t\t</li>')

    landmark_items.append(
        f"""\t\t\t\t<li>\n\t\t\t\t\t<a href="text/{first_chapter_file}" epub:type="bodymatter">{html.escape(metadata.title)}</a>\n\t\t\t\t</li>"""
    )
    landmark_items.append(
        '\t\t\t\t<li>\n\t\t\t\t\t<a href="toc.xhtml" epub:type="toc">Table of Contents</a>\n\t\t\t\t</li>'
    )
    landmark_items_str = "\n".join(landmark_items)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{metadata.language}" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="{metadata.language}">
	<head>
		<title>Table of Contents</title>
		<link href="css/core.css" rel="stylesheet" type="text/css"/>
		<link href="css/se.css" rel="stylesheet" type="text/css"/>
	</head>
	<body epub:type="frontmatter">
		<nav aria-labelledby="toc-title" id="toc" role="doc-toc" epub:type="toc">
			<h2 id="toc-title" epub:type="title">Table of Contents</h2>
			<ol>
{chapter_items_str}
			</ol>
		</nav>
		<nav aria-labelledby="landmarks-title" id="landmarks" epub:type="landmarks">
			<h2 id="landmarks-title" epub:type="title">Landmarks</h2>
			<ol>
{landmark_items_str}
			</ol>
		</nav>
	</body>
</html>"""


def get_toc_ncx(metadata: BookMetadata) -> str:
    nav_points = []
    play_order = 1

    if metadata.create_titlepage:
        nav_points.append(
            f"""\t\t<navPoint id="navpoint-{play_order}" playOrder="{play_order}">\n\t\t\t<navLabel>\n\t\t\t\t<text>Titlepage</text>\n\t\t\t</navLabel>\n\t\t\t<content src="text/titlepage.xhtml"/>\n\t\t</navPoint>"""
        )
        play_order += 1

    for ch in metadata.chapters:
        nav_points.append(
            f"""\t\t<navPoint id="navpoint-{play_order}" playOrder="{play_order}">\n\t\t\t<navLabel>\n\t\t\t\t<text>{html.escape(ch.title)}</text>\n\t\t\t</navLabel>\n\t\t\t<content src="text/{ch.output_filename}"/>\n\t\t</navPoint>"""
        )
        play_order += 1

    nav_map_str = "\n".join(nav_points)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="{metadata.language}">
	<head>
		<meta content="{metadata.uid}" name="dtb:uid"/>
	</head>
	<docTitle>
		<text>{html.escape(metadata.title)}</text>
	</docTitle>
	<navMap id="navmap">
{nav_map_str}
	</navMap>
</ncx>"""


def get_content_opf(metadata: BookMetadata) -> str:
    manifest_items = [
        '\t\t<item href="css/core.css" id="core.css" media-type="text/css"/>',
        '\t\t<item href="css/se.css" id="se.css" media-type="text/css"/>',
        '\t\t<item href="css/local.css" id="local.css" media-type="text/css"/>',
    ]

    cover_meta = ""
    cover_filename = metadata.cover_image.name if metadata.cover_image else None

    # Register images in manifest
    for img in metadata.images:
        mtype, _ = mimetypes.guess_type(img.name)
        if not mtype:
            ext = img.suffix.lower()
            if ext in {".jpg", ".jpeg"}:
                mtype = "image/jpeg"
            elif ext == ".png":
                mtype = "image/png"
            elif ext == ".webp":
                mtype = "image/webp"
            elif ext == ".svg":
                mtype = "image/svg+xml"
            elif ext == ".gif":
                mtype = "image/gif"
            else:
                mtype = "application/octet-stream"

        is_cover = cover_filename and img.name == cover_filename
        props = ' properties="cover-image"' if is_cover else ""
        manifest_items.append(
            f'\t\t<item href="images/{img.name}" id="{img.name}" media-type="{mtype}"{props}/>'
        )
        if is_cover:
            cover_meta = f'\t\t<meta name="cover" content="{img.name}"/>\n'

    # Titlepage in manifest only if enabled
    if metadata.create_titlepage:
        manifest_items.append(
            '\t\t<item href="text/titlepage.xhtml" id="titlepage.xhtml" media-type="application/xhtml+xml"/>'
        )

    # Chapters in manifest
    for ch in metadata.chapters:
        manifest_items.append(
            f'\t\t<item href="text/{ch.output_filename}" id="{ch.output_filename}" media-type="application/xhtml+xml"/>'
        )

    # TOC and NCX
    manifest_items.append(
        '\t\t<item href="toc.xhtml" id="toc.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
    )
    manifest_items.append(
        '\t\t<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>'
    )

    spine_items = []
    if metadata.create_titlepage:
        spine_items.append('\t\t<itemref idref="titlepage.xhtml"/>')
    for ch in metadata.chapters:
        spine_items.append(f'\t\t<itemref idref="{ch.output_filename}"/>')

    manifest_str = "\n".join(manifest_items)
    spine_str = "\n".join(spine_items)

    desc_element = f"\t\t<dc:description>{html.escape(metadata.description)}</dc:description>\n" if metadata.description else ""

    guide_items = []
    if metadata.create_titlepage:
        guide_items.append('\t\t<reference href="text/titlepage.xhtml" title="Titlepage" type="title-page"/>')
    guide_items.append('\t\t<reference href="toc.xhtml" title="Table of Contents" type="toc"/>')
    guide_str = "\n".join(guide_items)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" dir="ltr" prefix="rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#" unique-identifier="uid" version="3.0" xml:lang="{metadata.language}">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
		<dc:identifier id="uid">{metadata.uid}</dc:identifier>
		<dc:title id="title">{html.escape(metadata.title)}</dc:title>
		<dc:creator id="author">{html.escape(metadata.author)}</dc:creator>
		<meta property="file-as" refines="#author">{html.escape(metadata.author)}</meta>
		<meta property="role" refines="#author" scheme="marc:relators">aut</meta>
		<dc:language>{metadata.language}</dc:language>
		<dc:date>{metadata.pub_date}</dc:date>
		<meta property="dcterms:modified">{metadata.modified}</meta>
		<dc:rights>{html.escape(metadata.rights)}</dc:rights>
		<dc:publisher id="publisher">{html.escape(metadata.publisher)}</dc:publisher>
{desc_element}\t\t<meta id="conformance-statement" property="dcterms:conformsTo">EPUB Accessibility 1.1 - WCAG 2.2 Level AA</meta>
		<meta property="schema:accessMode">textual</meta>
		<meta property="schema:accessModeSufficient">textual</meta>
		<meta property="schema:accessibilityFeature">alternativeText</meta>
		<meta property="schema:accessibilityFeature">displayTransformability</meta>
		<meta property="schema:accessibilityFeature">readingOrder</meta>
		<meta property="schema:accessibilityFeature">structuralNavigation</meta>
		<meta property="schema:accessibilityFeature">tableOfContents</meta>
		<meta property="schema:accessibilityFeature">unlocked</meta>
		<meta property="schema:accessibilityHazard">none</meta>
		<meta property="schema:accessibilitySummary">This publication conforms to WCAG 2.2 Level AA.</meta>
{cover_meta}\t</metadata>
	<manifest>
{manifest_str}
	</manifest>
	<spine toc="ncx">
{spine_str}
	</spine>
	<guide>
{guide_str}
	</guide>
</package>"""


def get_local_css(metadata: BookMetadata) -> str:
    """
    Generates local.css with code block syntax highlighting and user custom styles.
    """
    pygments_css = HtmlFormatter(style="default").get_style_defs(".codehilite")

    base_local_css = f"""@charset "utf-8";
@namespace epub "http://www.idpf.org/2007/ops";

/* Code block & syntax highlighting */
pre {{
	background-color: #f6f8fa;
	border: 1px solid #d0d7de;
	border-radius: 6px;
	padding: 1em;
	overflow-x: auto;
	font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, monospace;
	font-size: 0.85em;
	line-height: 1.45;
	white-space: pre-wrap;
	word-break: break-word;
	margin-top: 1.5em;
	margin-bottom: 1.5em;
}}

code {{
	font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, monospace;
	font-size: 0.85em;
	background-color: #f0f2f5;
	padding: 0.2em 0.4em;
	border-radius: 3px;
}}

pre code {{
	background-color: transparent;
	padding: 0;
	font-size: inherit;
}}

{pygments_css}
"""
    custom_parts = []
    for css_file in metadata.custom_css:
        try:
            with open(css_file, "r", encoding="utf-8") as f:
                custom_parts.append(f"\n/* Custom CSS from {css_file.name} */\n" + f.read())
        except Exception as e:
            print(f"Warning: Failed to read custom CSS file '{css_file}': {e}", file=sys.stderr)

    return base_local_css + "\n".join(custom_parts)

# ==============================================================================
# Main Build Function
# ==============================================================================

def build_epub(
    book_dir_path: str | Path,
    output_file_path: Optional[str | Path] = None,
    force_titlepage: bool = False,
) -> Path:
    """
    Builds a Standard Ebooks-compliant EPUB 3 archive from book_dir_path.
    Requires 'book.yml' and a 'src/' folder inside book_dir_path.
    """
    book_dir = Path(book_dir_path).resolve()
    if not book_dir.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: '{book_dir}'")

    print(f"[*] Inspecting book directory: '{book_dir}'...")
    metadata = load_book_config(book_dir, force_titlepage=force_titlepage)
    print(f"    Title:    {metadata.title}")
    print(f"    Author:   {metadata.author}")
    print(f"    Language: {metadata.language}")
    print(f"    Found {len(metadata.chapters)} chapter(s) and {len(metadata.images)} image(s)")
    if metadata.cover_image:
        print(f"    Cover:    {metadata.cover_image.name} (Registered in manifest)")
    else:
        print("    Cover:    None")

    if not metadata.chapters:
        raise ValueError(f"No markdown chapters found in '{book_dir}/src'")

    # Determine output file path (default to current working directory)
    if output_file_path:
        out_path = Path(output_file_path).resolve()
    else:
        out_path = Path.cwd() / f"{book_dir.name}.epub"

    # Convert each chapter's Markdown to XHTML
    md_parser = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "footnotes", "smarty"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "smarty": {
                "smart_quotes": True,
                "smart_dashes": True,
                "smart_ellipses": True,
            },
        },
        output_format="xhtml",
    )

    print("[*] Processing chapters from 'src/'...")
    for idx, chapter in enumerate(metadata.chapters):
        with open(chapter.source_file, "r", encoding="utf-8") as f:
            raw_md = f.read()

        md_parser.reset()
        raw_html = md_parser.convert(raw_md)
        chapter.content_html = clean_and_format_xhtml(
            raw_html, chapter.title, has_heading_in_source=chapter.has_heading_in_source
        )
        print(f"    [{idx + 1:02d}/{len(metadata.chapters):02d}] {chapter.title} ({chapter.source_file.name})")

    # Generate XML/XHTML content
    container_xml = get_container_xml()
    content_opf = get_content_opf(metadata)
    toc_xhtml = get_toc_xhtml(metadata)
    toc_ncx = get_toc_ncx(metadata)
    local_css = get_local_css(metadata)

    # Packaging ZIP
    print(f"[*] Packaging EPUB archive to '{out_path}'...")
    with zipfile.ZipFile(out_path, "w") as zf:
        # 1. mimetype: MUST be first, uncompressed (ZIP_STORED) per EPUB OCF specification
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        zf.writestr("META-INF/container.xml", container_xml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        # 3. epub/content.opf
        zf.writestr("epub/content.opf", content_opf.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        # 4. epub/toc.xhtml (EPUB 3 Navigation)
        zf.writestr("epub/toc.xhtml", toc_xhtml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        # 5. epub/toc.ncx (EPUB 2 backward compatibility)
        zf.writestr("epub/toc.ncx", toc_ncx.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        # 6. Stylesheets
        zf.writestr("epub/css/core.css", CORE_CSS.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("epub/css/se.css", SE_CSS.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("epub/css/local.css", local_css.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        # 7. Images
        for img_path in metadata.images:
            with open(img_path, "rb") as f:
                img_data = f.read()
            zf.writestr(f"epub/images/{img_path.name}", img_data, compress_type=zipfile.ZIP_DEFLATED)

        # 8. Text documents: titlepage.xhtml (only if requested) and chapters
        if metadata.create_titlepage:
            titlepage_xhtml = get_titlepage_xhtml(metadata)
            zf.writestr("epub/text/titlepage.xhtml", titlepage_xhtml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

        for chapter in metadata.chapters:
            chapter_xhtml = get_chapter_xhtml(metadata, chapter)
            zf.writestr(f"epub/text/{chapter.output_filename}", chapter_xhtml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

    file_size_kb = out_path.stat().st_size / 1024
    print(f"[✓] Successfully generated EPUB: {out_path.name} ({file_size_kb:.1f} KB)")
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown directory to a Standard Ebooks-compliant EPUB 3 ebook. Requires 'book.yml' and a 'src/' folder."
    )
    parser.add_argument(
        "book_dir",
        help="Path to the book directory containing 'book.yml' and a 'src/' folder",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Optional output .epub file path (defaults to <book_dir_name>.epub in current directory)",
    )
    parser.add_argument(
        "--titlepage",
        action="store_true",
        help="Explicitly generate a synthetic titlepage document in the book spine",
    )

    args = parser.parse_args()
    try:
        build_epub(args.book_dir, args.output_file, force_titlepage=args.titlepage)
    except Exception as e:
        print(f"\n[Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
