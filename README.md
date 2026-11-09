# mark2epub

A Python tool for converting directories of Markdown files to high-quality EPUB 3 ebooks matching the typography and standards of Standard Ebooks.

## Description

`mark2epub` is a Python utility designed to convert Markdown documents, images, and custom stylesheets into standards-compliant, beautifully typeset **EPUB 3** ebooks. It directly incorporates the award-winning typography rules and layout stylesheets (`core.css`, `se.css`) developed by [Standard Ebooks](https://standardebooks.org), producing digital publications that render consistently and elegantly across reading systems such as Apple Books, Kobo, Kindle, and Calibre.

Every book project requires a configuration file (`book.yml`) and a source directory (`src/`) containing the chapter files and assets.

Key highlights:
* **Standard Ebooks Typography**: Built-in CSS with small-caps headings, elegant paragraph indentation, drop-caps, table styling, blockquotes, and optimized Dark Mode support.
* **Strict OCF & EPUB 3 Compliance**: Uncompressed `mimetype` (`ZIP_STORED`) written first at byte offset 0, ensuring 100% validity across EPUB validation tools.
* **Structured Book Layout**: Strict and predictable project structure requiring `book.yml` metadata and a `src/` content directory.
* **Natural Alphanumeric Sorting**: Orders numbered chapters naturally (`1. Introduction`, `2. Chapter`, ..., `9. Chapter`, `10. Movement`).
* **Clean Cover Handling**: Cover images are registered in the package manifest as `properties="cover-image"` for reader library shelves without injecting awkward synthetic cover pages into the text flow.
* **Smart Typography**: Automatic conversion of straight quotes to curly quotes (`“ ”`, `‘ ’`), dashes (`—`, `–`), and ellipses (`…`).
* **Code Syntax Highlighting**: Integrated Pygments styling for syntax-highlighted code blocks (`:::python`, fenced code).
* **Dual Navigation**: Builds an EPUB 3 Navigation Document (`toc.xhtml` with landmarks) alongside a backwards-compatible NCX (`toc.ncx`).
* **Accessibility**: Embedded WCAG 2.2 Level AA / EPUB Accessibility 1.1 metadata.

## Getting Started

### Dependencies

* Python 3.8 or higher
* Operating System: Linux, macOS, or Windows
* Python libraries:
  * `markdown` (>= 3.1)
  * `PyYAML` (>= 6.0)
  * `beautifulsoup4` (>= 4.11)
  * `Pygments` (>= 2.14)

### Installing

1. Clone or download this repository:
```bash
git clone https://github.com/willfreee/mark2epub.git
cd mark2epub
```

2. Install the necessary Python packages:
```bash
pip install markdown PyYAML beautifulsoup4 Pygments
```

### Executing program

#### 1. Required Project Structure
The target book folder **must** contain a `book.yml` configuration file and a `src/` directory holding your Markdown chapters and optional assets:

```text
my-book/
├── book.yml
└── src/
    ├── chapter1.md
    ├── chapter2.md
    ├── css/                # Optional custom CSS
    │   └── custom.css
    └── images/             # Optional images
        └── cover.jpg
```

#### 2. Configuration (`book.yml`)
Define your book metadata and chapter order in `book.yml`:
```yaml
title: Pride and Prejudice
author: Jane Austen
description: A classic novel of manners.
language: en
cover: images/cover.jpg
chapters:
  - 'Chapter 1': chapter1.md
  - 'Chapter 2': chapter2.md
```

> **Note**:
> * If `chapters` is omitted, `mark2epub` will automatically include all `.md` files found in `src/`, sorted in natural numerical order.
> * If `cover` is not specified, `mark2epub` automatically searches `src/images/` or `src/` for `cover.jpg`, `cover.png`, or `cover.webp`.

#### 3. Running the Converter
Run `mark2epub` by pointing to the book directory (supports both relative and absolute paths):

```bash
# Convert a local book folder (outputs <folder_name>.epub in current directory)
python3 mark2epub.py path/to/my-book/

# Specify a custom output file name or path
python3 mark2epub.py path/to/my-book/ output-book.epub
```

#### 4. Command-line Options
```bash
# Explicitly generate a synthetic titlepage inside the book spine
python3 mark2epub.py path/to/my-book/ --titlepage

# Display command-line help
python3 mark2epub.py --help
```

## Help

Common issues and troubleshooting tips:

* **Missing `book.yml` or `src/` error**:
  `mark2epub` strictly requires both `book.yml` and the `src/` folder to be present at the root of the book directory. Ensure your directory follows the required layout.
* **Missing dependencies error**:
  Run `pip install markdown PyYAML beautifulsoup4 Pygments` to ensure all required libraries are installed in your active Python environment.
* **Image path resolution**:
  Images referenced in Markdown as `images/sample.png` or `![diagram](images/sample.png)` are automatically normalized to `../images/sample.png` in the compiled XHTML chapters.
* **Cover images**:
  When a cover image is detected, it is registered with `properties="cover-image"` in the EPUB manifest. E-readers will display it as the book thumbnail on your library shelf.

```bash
python3 mark2epub.py -h
```

## Authors

* **Duy Khanh** - *Maintainer & Developer* - [@duykhanh471](https://github.com/duykhanh471)
* **Standard Ebooks** - *Typography stylesheets & EPUB standards* - [standardebooks.org](https://standardebooks.org)

## Version History

* 0.3
    * Enforced mandatory `book.yml` configuration and `src/` content directory
    * Removed synthetic cover page by default; cover images are registered via manifest metadata
    * Implemented natural alphanumeric sorting (1, 2, ..., 9, 10)
    * Integrated Standard Ebooks EPUB 3 architecture, accessibility metadata, and typography stylesheets
    * Added `--titlepage` flag for optional titlepage generation
* 0.2
    * Added `book.yml` support and code block syntax highlighting
* 0.1
    * Initial release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

* [Standard Ebooks](https://standardebooks.org) for their open-source typography stylesheets and EPUB design guidelines
* [Python-Markdown](https://python-markdown.github.io/)
* [Pygments](https://pygments.org/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [readme-template](https://github.com/dbader/readme-template)
