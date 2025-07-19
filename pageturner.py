import argparse
import logging
import os
import sys
import yaml
import re # Import re for regex operations

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define a default output filename constant
DEFAULT_OUTPUT_FILENAME = "output.epub"

def _sanitize_filename(title: str) -> str:
    """
    Sanitizes a string to be used as a filename:
    - Converts to lowercase.
    - Replaces spaces with underscores.
    - Removes characters that are not alphanumeric, underscores, or hyphens.
    - Trims leading/trailing underscores/hyphens.
    """
    # Convert to lowercase
    filename = title.lower()
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    filename = re.sub(r'[^\w-]', '', filename)
    # Replace multiple consecutive underscores/hyphens with a single one
    filename = re.sub(r'[_]+', '_', filename)
    filename = re.sub(r'[-]+', '-', filename)
    # Trim leading/trailing underscores/hyphens
    filename = filename.strip('_-')
    return filename + ".epub"


def main():
    """
    Main function to parse arguments and start the web novel conversion process.
    """
    parser = argparse.ArgumentParser(
        description="Convert web novels to Kindle-friendly EPUBs."
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file for the novel (default: config.yaml)."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILENAME, # Use the constant here
        help="Name of the output EPUB file (e.g., my_novel.epub). "
             "Defaults to a sanitized version of the novel title."
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (e.g., DEBUG, INFO)."
    )

    args = parser.parse_args()

    # Set logging level based on user input
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    for handler in logging.root.handlers:
        handler.setLevel(log_level)

    logger.info("pageturner started.")
    logger.info(f"Using configuration file: {args.config}")
    # logger.info(f"Output EPUB file: {args.output}") # We'll log this after potential change

    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)

    config = {}
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully.")

        # Basic validation for essential config keys
        if not all(k in config for k in ['novel_title', 'start_url', 'content_selectors']) or \
           'next_chapter_selectors' not in config or \
           not any(s.get('type') == 'url_pattern' for s in config['next_chapter_selectors']):
            logger.error("Configuration missing essential keys. Required: novel_title, start_url, content_selectors, and a 'url_pattern' in next_chapter_selectors.")
            sys.exit(1)

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading config: {e}")
        sys.exit(1)

    logger.debug(f"Configuration content: {config}")

    # --- NEW: Automatically set output filename if not provided ---
    if args.output == DEFAULT_OUTPUT_FILENAME:
        novel_title_from_config = config.get('novel_title', 'untitled_novel')
        sanitized_filename = _sanitize_filename(novel_title_from_config)
        args.output = sanitized_filename
        logger.info(f"Output EPUB file automatically set to: {args.output} (from novel title).")
    else:
        logger.info(f"Output EPUB file explicitly set to: {args.output}.")


    # --- Import all core modules ---
    from src.core.page_loader import PageLoader
    from src.core.chapter_navigator import URLChapterNavigator
    from src.core.content_extractor import ContentExtractor
    from src.core.epub_generator import EpubGenerator

    chapter_contents = []
    processed_urls = set()

    consecutive_empty_chapters = 0
    empty_chapter_threshold = config.get('consecutive_empty_chapters_threshold', 3)

    try:
        loader = PageLoader()

        url_pattern_config = next((s for s in config['next_chapter_selectors'] if s.get('type') == 'url_pattern'), None)
        navigator = URLChapterNavigator(
            start_url=config['start_url'],
            url_pattern=url_pattern_config['pattern'],
            increment_by=url_pattern_config.get('increment_by', 1)
        )

        extractor = ContentExtractor(
            content_selectors=config['content_selectors'],
            remove_elements=config.get('remove_elements', []),
            chapter_title_selector=config.get('chapter_title_selector')
        )

        current_chapter_url = navigator.get_start_url()
        chapter_number = 1

        while current_chapter_url:
            if current_chapter_url in processed_urls:
                logger.warning(f"Detected a URL loop: '{current_chapter_url}' already processed. Stopping.")
                break
            processed_urls.add(current_chapter_url)

            logger.info(f"Processing Chapter {chapter_number}: {current_chapter_url}")

            chapter_html = loader.fetch_page(current_chapter_url)

            if chapter_html:
                extracted_title, extracted_content = extractor.extract_content(chapter_html)

                if extracted_content:
                    logger.debug(f"Extracted content for chapter {chapter_number} (first 200 chars): {extracted_content[:200]}...")

                    chapter_title_to_use = extracted_title if extracted_title else f"Chapter {chapter_number}"

                    chapter_contents.append({
                        "title": chapter_title_to_use,
                        "html_content": extracted_content
                    })
                    consecutive_empty_chapters = 0
                else:
                    logger.warning(f"No main content extracted for chapter {chapter_number} from {current_chapter_url}.")
                    consecutive_empty_chapters += 1
                    if consecutive_empty_chapters >= empty_chapter_threshold:
                        logger.warning(f"Reached {empty_chapter_threshold} consecutive chapters with no main content. Assuming end of novel or invalid chapter sequence. Stopping.")
                        break
                    logger.info(f"Consecutive empty chapters: {consecutive_empty_chapters}/{empty_chapter_threshold}")

                next_url = navigator.get_next_chapter_url(current_chapter_url)
                if next_url is None:
                    logger.info("Chapter navigator indicated no next URL. Stopping processing.")
                    break
                current_chapter_url = next_url
                chapter_number += 1
            else:
                logger.warning(f"Failed to fetch content for {current_chapter_url}. This might indicate the end of the novel or a site issue. Stopping novel processing.")
                break

        logger.info(f"Finished fetching chapters. Total chapters extracted: {len(chapter_contents)}")

        if chapter_contents:
            generator = EpubGenerator(
                novel_title=config['novel_title'],
                novel_author=config.get('novel_author', 'Unknown'),
                language=config.get('language', 'en'),
                output_path=args.output, # Use the (potentially modified) output path
                cover_image_url=config.get('cover_image_url'), # Pass cover image URL
                page_loader=loader # Pass the PageLoader instance
            )
            generator.add_chapters(chapter_contents)
            generator.generate_epub()
        else:
            logger.warning("No chapters were extracted, so no EPUB will be generated.")

    except Exception as e:
        logger.error(f"An error occurred during novel processing: {e}", exc_info=True)
        sys.exit(1)

    logger.info("pageturner process finished.")


if __name__ == "__main__":
    main()