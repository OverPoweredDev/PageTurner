# pageturner

## 📖 Turn Web Novels into Kindle-Ready EPUBs

`pageturner` is a powerful Python-based utility designed to streamline your web novel reading experience. It scrapes web novels from various online platforms and converts them into clean, readable EPUB files, perfectly formatted for your Kindle or other e-readers. Say goodbye to distracting ads, inconsistent formatting, and manual copying – enjoy your favorite stories seamlessly!

### ✨ Features

* **Configurable Conversion:** All settings are managed through a single, easy-to-edit `config.yaml` file, allowing you to adapt `pageturner` to different web novel sites.
* **URL-Based Chapter Navigation:** Automatically progresses through novel chapters by intelligently incrementing chapter numbers found in URLs.
* **Intelligent Content Extraction:** Uses robust selectors to identify and extract the main story content from web pages, filtering out unwanted elements like headers, footers, and advertisements.
* **Dynamic Chapter Titles:** Optionally extracts actual chapter titles from the web page using configurable selectors, enhancing the EPUB's readability and navigation.
* **Smart Stop Conditions:** Prevents infinite loops by stopping processing if a configurable number of consecutive chapters yield no main content, or if a URL loop is detected.
* **Rich EPUB Metadata:**
    * Sets the EPUB title and author from your configuration.
    * Includes a novel description.
    * Sets "Pageturner" as the publisher.
    * Supports a **cover image** by downloading an image from a provided URL and embedding it as the EPUB's cover.
* **Automated Output Filename:** Generates a clean, descriptive output EPUB filename based on the novel's title from your configuration, making file organization a breeze.
* **Modular Design:** Built with a clear separation of concerns, making it easy to extend and maintain.

### 🚀 Getting Started

#### Prerequisites

* Python 3.8+ (You're using 3.13, which is great!)
* `pip` (Python package installer)

#### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/OverPoweredDev/pageturner.git](https://github.com/OverPoweredDev/pageturner.git)
    cd pageturner
    ```
2.  **Create a virtual environment (highly recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: `venv\Scripts\activate`
    ```
3.  **Install the required packages:**
    ```bash
    pip install requests beautifulsoup4 lxml pyyaml EbookLib
    ```

#### Usage

1.  **Prepare your `config.yaml`:**
    Create a `config.yaml` file in the root of your `pageturner` directory. This file will define all the necessary settings for the novel you want to convert.

    Here's an example `config.yaml` structure:

    ```yaml
    # General Novel Information
    novel_title: "My Awesome Web Novel"
    novel_author: "Author Name"
    language: "en" # EPUB language code (e.g., 'en', 'fr', 'zh-CN')

    # Optional novel description
    description: "A thrilling story of adventure and discovery in a magical realm."

    # Optional cover image URL
    # If provided, this image will be downloaded and used as the EPUB cover.
    # Example: cover_image_url: "[https://example.com/novel/cover.jpg](https://example.com/novel/cover.jpg)"
    cover_image_url: "[https://via.placeholder.com/400x600.png?text=My+Novel+Cover](https://via.placeholder.com/400x600.png?text=My+Novel+Cover)"

    # Stopping Conditions
    # Stop if this many consecutive chapters yield no main content.
    consecutive_empty_chapters_threshold: 3

    # Starting URL of the first chapter
    # IMPORTANT: Ensure this URL follows a numeric pattern for URL-based navigation.
    start_url: "http://localhost:8000/chapter-1.html" # Example for local testing

    # Page Loading Strategy (currently only 'requests' is supported for direct HTTP fetching)
    page_loader: "requests"

    # Chapter Navigation Strategy
    # Currently focuses on 'url_pattern' to increment chapter numbers in the URL.
    next_chapter_selectors:
      - type: "url_pattern"
        # Regex pattern to capture the numerical part of the chapter URL.
        # The first capturing group (e.g., (\d+)) should be the number to increment.
        pattern: "(chapter-(\d+)\\.html)" # Example for /chapter-1.html, /chapter-2.html
        increment_by: 1 # How much to increment the matched number

    # Content Extraction Strategy
    # Defines how to find the main story content on each page.
    content_selectors:
      - type: "css_selector"
        selector: "div#chapter-content" # Common CSS selector for content area

    # Optional: Selector to find the chapter title within the page's HTML
    # If not provided, chapters will be named "Chapter 1", "Chapter 2", etc.
    chapter_title_selector: "h1.chapter-title" # Example selector: adjust for actual site

    # Optional: Elements to remove from the extracted content (e.g., ads, internal navigation)
    remove_elements:
      - "div.ads"
      - "span.editor-note"
    ```
    You can find example configurations in the `config_examples/` directory (once you add them).

2.  **Run `pageturner`:**
    Execute the script from your terminal in the project root.

    ```bash
    python pageturner.py --config config.yaml --output my_novel.epub --log-level INFO
    ```

    * `--config config.yaml`: Specifies your configuration file. (Defaults to `config.yaml` if omitted).
    * `--output my_novel.epub`: Specifies the output filename. (Defaults to a sanitized version of `novel_title` if omitted).
    * `--log-level INFO`: Controls verbosity (use `DEBUG` for more detailed output during development).
