import logging
from ebooklib import epub
from bs4 import BeautifulSoup
import os # For path manipulation (image extension)
from urllib.parse import urlparse # To get filename from URL

logger = logging.getLogger(__name__)

class EpubGenerator:
    """
    Generates an EPUB file from a list of chapter HTML contents.
    Includes support for novel description, publisher, and cover image from URL.
    """
    def __init__(self, novel_title: str, novel_author: str, language: str, output_path: str,
                 cover_image_url: str = None, page_loader=None): # Added page_loader
        """
        Initializes the EpubGenerator.

        Args:
            novel_title (str): The title of the novel.
            novel_author (str): The author of the novel.
            language (str): The language code for the EPUB (e.g., 'en', 'fr').
            output_path (str): The file path where the EPUB will be saved.
            description (str, optional): A brief summary of the novel. Defaults to None.
            cover_image_url (str, optional): URL to a cover image. Defaults to None.
            page_loader: An instance of PageLoader to download the cover image.
        """
        self.book = epub.EpubBook()
        self.novel_title = novel_title
        self.novel_author = novel_author
        self.language = language
        self.output_path = output_path
        self.cover_image_url = cover_image_url
        self.page_loader = page_loader # Store the PageLoader instance

        self.chapters = []
        self.toc_items = []

        self._set_metadata()
        logger.debug(f"EpubGenerator initialized for '{novel_title}' by '{novel_author}'.")

    def _set_metadata(self):
        """Sets the basic metadata for the EPUB book."""
        # A UUID is a good practice for identifier
        # from uuid import uuid4
        # self.book.set_identifier(str(uuid4()))
        self.book.set_identifier(self.output_path.split('/')[-1].replace('.epub', '')) # Simple identifier

        self.book.set_title(self.novel_title)
        self.book.add_author(self.novel_author)
        self.book.set_language(self.language)

        logger.debug("EPUB basic metadata set.")

    def _add_cover_image(self):
        """
        Downloads the cover image from the URL and adds it to the EPUB.
        Requires a PageLoader instance to download the image.
        """
        if not self.cover_image_url or not self.page_loader:
            logger.debug("No cover image URL or PageLoader provided. Skipping cover.")
            return

        logger.info(f"Attempting to download cover image from: {self.cover_image_url}")
        image_bytes = self.page_loader.fetch_image_bytes(self.cover_image_url)

        if image_bytes:
            # Determine image type from URL extension or headers if necessary
            parsed_url = urlparse(self.cover_image_url)
            # Get extension from path, defaulting to .jpg if none found
            ext = os.path.splitext(parsed_url.path)[1].lower() or '.jpg'
            if ext == '.jpeg': ext = '.jpg' # Normalize jpeg to jpg

            # Determine media type for epub.EpubItem
            media_type = f"image/{ext.lstrip('.')}"
            if ext not in ['.jpg', '.png', '.gif']: # Basic validation
                logger.warning(f"Unsupported cover image format: {ext}. Skipping cover.")
                return

            cover_filename = f'cover{ext}' # Always name the cover file 'cover.ext'
            cover_item = epub.EpubItem(
                uid="cover",
                file_name=cover_filename,
                media_type=media_type,
                content=image_bytes
            )
            self.book.add_item(cover_item)
            self.book.set_cover(cover_filename, image_bytes)
            logger.info(f"Cover image '{cover_filename}' added successfully.")
        else:
            logger.warning(f"Failed to download cover image from {self.cover_image_url}.")


    def add_chapters(self, chapter_data_list: list):
        """
        Adds a list of chapter HTML contents to the EPUB book.
        """
        for i, chapter_data in enumerate(chapter_data_list):
            chapter_title = chapter_data.get("title", f"Chapter {i+1}")
            html_content = chapter_data.get("html_content")

            if not html_content:
                logger.warning(f"No HTML content for '{chapter_title}', skipping chapter.")
                continue

            chapter_id = f'chap_{i+1}'
            chapter_file_name = f'chapter_{i+1}.xhtml'

            c = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang=self.language)

            soup = BeautifulSoup(html_content, 'html.parser')
            # Ensure content is inside a body tag for valid XHTML
            if soup.body:
                 c.content = str(soup.body)
            else:
                c.content = f'<body>{str(soup)}</body>'
            
            self.book.add_item(c)
            self.chapters.append(c)
            self.toc_items.append(epub.Link(chapter_file_name, chapter_title, chapter_id))
            logger.debug(f"Added chapter: '{chapter_title}' ({chapter_file_name})")

        logger.info(f"All {len(self.chapters)} chapters added to EPUB.")

    def generate_epub(self):
        """
        Finalizes the EPUB structure and writes the file to the specified path.
        """
        # Add cover image before finalizing structure
        self._add_cover_image()

        self.book.toc = self.toc_items
        self.book.spine = ['nav'] + self.chapters # 'nav' is for the auto-generated navigation document

        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        try:
            epub.write_epub(self.output_path, self.book, {})
            logger.info(f"EPUB file '{self.output_path}' generated successfully!")
        except Exception as e:
            logger.error(f"Failed to generate EPUB file '{self.output_path}': {e}", exc_info=True)
            raise