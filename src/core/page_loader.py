import requests
import logging

logger = logging.getLogger(__name__)

class PageLoader:
    """
    Handles fetching HTML content and raw image bytes from a given URL using the requests library.
    """
    def __init__(self):
        logger.debug("PageLoader initialized (using requests only).")

    def fetch_page(self, url: str) -> str | None:
        """
        Fetches the HTML content of a given URL using the requests library.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.debug(f"Successfully fetched URL: {url} with requests.")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url} with requests: {e}")
            return None

    def fetch_image_bytes(self, url: str) -> bytes | None:
        """
        Fetches raw image bytes from a given URL.

        Args:
            url (str): The URL of the image.

        Returns:
            bytes | None: The raw image bytes, or None if fetching fails.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.debug(f"Successfully fetched image: {url}")
            return response.content # .content gets raw bytes
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image {url}: {e}")
            return None

    def close(self):
        """
        No specific resources to close when using requests only.
        """
        logger.debug("PageLoader (requests) has no resources to close.")