# 🌐 Web Scraper Toolkit

A modern Python desktop application for extracting, processing, and exporting web data with an intuitive graphical interface.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-MVP-brightgreen)

---

## 📖 Overview

Web Scraper Toolkit is a Python-based desktop application designed to simplify web data extraction.

Instead of writing a custom scraping script for every website, you point it at one or many URLs, give it a CSS selector or an XPath expression, and it extracts the matching text (or attribute, e.g. `href`) from each page and exports the results to CSV, Excel or JSON.

The project focuses on usability, clean architecture, and reliability — one bad URL never stops a batch, and every request respects the target site's `robots.txt` by default.

---

## ✨ Features

- 🌐 Single-page and multi-page (batch) scraping — one URL per line
- 🔍 CSS Selector support
- 📌 XPath support (including expressions that select an attribute directly, e.g. `//a/@href`)
- 🏷️ Extract an element's text, or a specific attribute (e.g. `href`, `src`)
- 📄 Export to CSV
- 📊 Export to Excel
- 📦 Export to JSON
- 🔄 Automatic retries on connection errors and 5xx responses (client errors like 404 are not retried)
- 🤖 Robots.txt awareness — disallowed pages are skipped automatically (can be turned off)
- ⚙️ Configurable User-Agent, timeout and retry count
- 🖥️ Modern PySide6 desktop interface with a progress bar and a live log

---

## 🛠️ Technologies

- Python 3.13
- PySide6 (desktop interface)
- Requests (HTTP)
- lxml + cssselect (HTML parsing, CSS/XPath selection)
- Pandas + OpenPyXL (CSV / Excel / JSON export)
- pytest (automated tests)
- PyInstaller (Windows `.exe` build)

---

## 📂 Project Structure

```
Python Web Scraper/
│
├── app.py                  # Entry point
├── app.spec                # PyInstaller build spec
├── core/
│   ├── http_client.py      # Fetching (User-Agent, timeout, retries)
│   ├── parser.py           # CSS/XPath extraction
│   └── scraper.py          # Ties fetch + parse together, batch + robots.txt
├── services/
│   └── export_service.py   # CSV / Excel / JSON export
├── gui/
│   └── main_window.py      # PySide6 interface
├── tests/                  # pytest unit tests
├── README.md
├── ROADMAP.txt
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## 📥 Installation

Clone the repository

```bash
git clone https://github.com/halittiryakicom/web-scraper-toolkit.git
```

Go to the project directory

```bash
cd web-scraper-toolkit
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

## 🚀 Usage

1. Paste one or more URLs into the **URLs** box (one per line).
2. Enter a **CSS selector** (e.g. `h2.title`) or switch to **XPath** (e.g. `//h2[@class='title']`).
3. Optionally set an **Attribute** (e.g. `href`) to extract a link target instead of text.
4. Pick an export **format** and output **folder**, then click **Scrape**.
5. Results are saved as `scrape_results.csv` / `.xlsx` / `.json` in the chosen folder.

---

## 🧪 Tests

```bash
pip install pytest
pytest tests -q
```

---

## 🚀 Roadmap

Current version: `v0.5.0` — core scraping engine, export, batch processing and the desktop GUI are done.

Still planned:

- Multi-page crawling (follow links)
- Proxy support
- Selenium integration (JavaScript-rendered pages)
- Persisted project settings
- Scheduled scraping

See **ROADMAP.txt** for detailed planning.

---

## 🎯 Project Goals

- Simplify web scraping workflows
- Reduce repetitive scraping tasks
- Export structured datasets efficiently
- Provide an intuitive desktop experience
- Demonstrate clean Python application architecture

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Halit Tiryaki**

🌐 Website

https://halittiryaki.com

🐙 GitHub

https://github.com/halittiryakicom

---

⭐ If you find this project useful, consider giving it a star!
