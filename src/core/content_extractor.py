import logging
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    Extracts the main novel content and an optional chapter title from HTML
    using configured selectors.
    """
    def __init__(self, content_selectors: list, remove_elements: list = None, chapter_title_selector: str = None):
        """
        Initializes the ContentExtractor.

        Args:
            content_selectors (list): A list of dictionaries, each defining a
                                      CSS selector strategy to find the main content.
            remove_elements (list, optional): A list of CSS selectors for elements
                                              to remove from the extracted content. Defaults to None.
            chapter_title_selector (str, optional): A CSS selector to find the
                                                    chapter title. Defaults to None.
        """
        if not content_selectors:
            raise ValueError("content_selectors cannot be empty.")
        self.content_selectors = content_selectors
        self.remove_elements = remove_elements if remove_elements is not None else []
        self.chapter_title_selector = chapter_title_selector # Store the new selector

        logger.debug(f"ContentExtractor initialized with content_selectors: {self.content_selectors}")
        logger.debug(f"Remove elements: {self.remove_elements}")
        logger.debug(f"Chapter title selector: {self.chapter_title_selector}")

    def extract_content(self, html_content: str) -> tuple[str | None, str | None]:
        """
        Parses the HTML content and extracts the main novel text and optional title.

        Args:
            html_content (str): The raw HTML content of the chapter page.

        Returns:
            tuple[str | None, str | None]: A tuple containing (extracted_title_text, extracted_content_html).
                                           Returns (None, None) if main content cannot be found.
        """
        if not html_content:
            logger.warning("No HTML content provided for extraction.")
            return None, None

        soup = BeautifulSoup(html_content, 'lxml') # Use 'lxml' parser for speed

        # --- Extract Chapter Title (Optional) ---
        extracted_title = None
        if self.chapter_title_selector:
            title_tag = soup.select_one(self.chapter_title_selector)
            if title_tag:
                extracted_title = title_tag.get_text(strip=True)
                logger.debug(f"Extracted chapter title: '{extracted_title}' using selector: '{self.chapter_title_selector}'")
            else:
                logger.debug(f"No chapter title found using selector: '{self.chapter_title_selector}'")

        # --- Extract Main Content ---
        main_content_tag = None
        for selector_config in self.content_selectors:
            selector_type = selector_config.get('type')
            selector_value = selector_config.get('selector')

            if not selector_type or not selector_value:
                logger.warning(f"Invalid content selector configuration: {selector_config}. Skipping.")
                continue

            if selector_type == "css_selector":
                found_tag = soup.select_one(selector_value)
                if found_tag:
                    main_content_tag = found_tag
                    logger.debug(f"Main content found using CSS selector: '{selector_value}'")
                    break
                else:
                    logger.debug(f"No main content found with CSS selector: '{selector_value}'")
            else:
                logger.warning(f"Unsupported content selector type: {selector_type}. Skipping.")

        if not main_content_tag:
            logger.error("Could not find any main content using the configured selectors.")
            return extracted_title, None # Return title if found, but no content

        # Apply removal rules to the found content
        self._remove_unwanted_elements(main_content_tag)

        return extracted_title, str(main_content_tag)

    def _remove_unwanted_elements(self, content_tag: Tag):
        """
        Removes specified elements from within the main content tag.
        """
        for selector in self.remove_elements:
            for element_to_remove in content_tag.select(selector):
                logger.debug(f"Removing element matching selector: '{selector}'")
                element_to_remove.decompose()