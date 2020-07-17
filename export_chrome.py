import logging
import argparse
import pgbookmarks
from pgbookmarks.pglogger import logger


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.description = """
Processes a Google Chrome bookmarks JSON file into custom text-file /
directory-based text bookmarks format.

Each folder of bookmarks is represented as a text file, first-level sub-folders
of the root "Bookmarks Bar" are represented as .txt files, and with deeper
sub-folders placed into directories.

Starting with the root "bookmarks bar" bookmarks.txt:
export/chrome_bookmarks_TIMESTAMP/bookmarks.txt
export/chrome_bookmarks_TIMESTAMP/SUBFOLDER.txt
export/chrome_bookmarks_TIMESTAMP/SUBFOLDER/DEEPER_SUBFOLDER.txt
export/chrome_bookmarks_TIMESTAMP/SUBFOLDER/DEEPER_SUBFOLDER/EVEN_DEEPER.txt

File format; bookmark titles and urls separated by a newline, each bookmark
separated by multiple newlines:

    Bookmark Title
    http://example.com/bookmark_url

    Another Bookmark Title
    http://example.com/another_bookmark_url
    optional note value

Allows rapid copy+paste placement of new bookmarks without requiring
encapsulating characters, or formatting issues when hand-editing a textual data
structure like JSON.

Note: no startpage.columns file is created.

OSX Chome default Bookmark location:
/Users/<USERNAME>/Library/Application Support/Google/Chrome/Default/Bookmarks
"""
    parser.epilog = "CAUTION: program does not delete files between runs."

    parser.add_argument("chrome_bookmarks_path",
                        metavar="chrome-bookmarks-path",
                        help="Location of Chrome bookmarks JSON file.")

    parser.add_argument("output_directory",
                        metavar="output-directory",
                        help="Directory to write Bookmarks files to.")

    parser.add_argument("-v", "--verbosity", action="store_true",
                        help="Increases verbosity, sets logging to DEBUG.")

    parser.add_argument("--dry-run", action='store_true',
                        help="Reads and processess site, skips writing files.")

    parser.print_usage = parser.print_help
    args = parser.parse_args()

    if args.verbosity:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)

    chrome_bc = pgbookmarks.LoadBookmarksFromChrome(args.chrome_bookmarks_path)
    if not args.dry_run:
        chrome_bc.ExportToFilesystem(args.output_directory)


if __name__ == '__main__':
    main()
