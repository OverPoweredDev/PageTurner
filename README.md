# PageTurner

## 📖 Turn Web Novels into Kindle-Ready EPUBs

`pageturner` is a Python-based utility designed to scrape web novels from various online platforms and convert them into clean, readable EPUB files, perfectly formatted for your Kindle or other e-readers. Say goodbye to distracting ads and inconsistent formatting – enjoy your favorite stories seamlessly!

### ✨ Features

* **Configurable Navigation:** Adapt to different website structures by defining how `pageturner` should find the next chapter (e.g., URL patterns, "Next" buttons, specific selectors).
* **Intelligent Content Extraction:** Aims to automatically identify and extract the main story content from web pages, filtering out unwanted elements like headers, footers, and ads.
* **EPUB Generation:** Creates well-structured EPUB files complete with chapter breaks and metadata.
* **Flexible Page Loading:** Choose between fast, direct fetching for static sites or robust, browser-driven rendering for dynamic, JavaScript-heavy pages.
* **Input via Configuration File:** Initially, define your scraping rules and starting URLs using a simple input file.
* **Future UI Plans:** Designed with a modular architecture to easily integrate a user interface later on.
