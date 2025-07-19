import re
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class URLChapterNavigator:
    """
    Navigates to the next chapter by incrementing a number found in the URL pattern.
    """
    def __init__(self, start_url: str, url_pattern: str, increment_by: int = 1):
        """
        Args:
            start_url (str): The URL of the first chapter.
            url_pattern (str): A regex pattern that contains a capturing group (e.g., (\d+))
                                for the chapter number to be incremented.
                                Example: "(/chapter-(\\d+)\\.html)"
            increment_by (int): The value to increment the chapter number by.
        """
        self.start_url = start_url
        self.url_pattern = url_pattern
        self.increment_by = increment_by
        self._base_url = self._get_base_url(start_url)

    def _get_base_url(self, url: str) -> str:
        """Extracts the base URL (scheme and netloc) from a full URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_start_url(self) -> str:
        """Returns the configured start URL."""
        return self.start_url

    def get_next_chapter_url(self, current_url: str) -> str | None:
        """
        Attempts to find the chapter number in the current URL using the pattern
        and construct the next chapter's URL by incrementing that number.

        Args:
            current_url (str): The URL of the current chapter.

        Returns:
            str | None: The URL of the next chapter, or None if the pattern
                        is not found or an error occurs.
        """
        match = re.search(self.url_pattern, current_url)
        if match:
            try:
                # The captured group is the chapter number, should be an integer
                current_chapter_num = int(match.group(2) if len(match.groups()) > 1 else match.group(1))
                next_chapter_num = current_chapter_num + self.increment_by

                # To handle `(/chapter-(\d+)\.html)` where `(\d+)` is the second group:
                segment_to_replace = match.group(1) # e.g., /chapter-1.html
                # Replace the number within that segment
                new_segment = re.sub(f"(\\d+)", str(next_chapter_num), segment_to_replace, count=1)

                # Now, replace the old segment in the full URL
                next_url = current_url.replace(segment_to_replace, new_segment, 1)

                logger.debug(f"Current URL: {current_url}, Pattern: '{self.url_pattern}', Match: {match.groups()}")
                logger.debug(f"Extracted num: {current_chapter_num}, Next num: {next_chapter_num}, Next URL: {next_url}")

                # Basic check to prevent infinite loops on non-incrementing URLs or edge cases
                if next_url == current_url:
                    logger.warning(f"Next URL is identical to current URL ({current_url}). Stopping navigation.")
                    return None

                return next_url
            except ValueError:
                logger.error(f"Chapter number found by pattern '{self.url_pattern}' is not an integer in URL: {current_url}")
                return None
            except IndexError:
                logger.error(f"Regex pattern '{self.url_pattern}' does not have a capturing group for the chapter number.")
                return None
        else:
            logger.info(f"URL pattern '{self.url_pattern}' not found in '{current_url}'. Assuming end of novel.")
            return None