import os
import logging
import argparse

import pgbookmarks
from pgbookmarks.pglogger import logger


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.description = """
Writes the HTML file and handles the static files that create a start page
from the standard bookmarks textfiles.
"""
    parser.epilog = "Program overrwites files each run."

    parser.add_argument("source_directory", metavar="source-directory",
                        help="Directory containing bookmarks text files.",
                        default="main_bookmarks")

    parser.add_argument("output_directory", metavar="output-directory",
                        help="Output directory for generated start page.",
                        default="startpage")

    parser.add_argument("-d", "--download-favicons", action="store_true",
                        help="Optionally attempt to download favicons.")

    parser.add_argument("-v", "--verbosity", action="store_true",
                        help="Increases verbosity, sets logging to DEBUG.")

    parser.add_argument("--dry-run", action='store_true',
                        help="Reads and processess site, skips writing files.")

    args = parser.parse_args()

    if args.verbosity:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)

    logger.debug("Debug: ON")

    source_directory = os.path.abspath(args.source_directory)
    output_directory = os.path.abspath(args.output_directory)
    static_directory = os.path.abspath('static')

    main_bc = pgbookmarks.LoadBookmarksFromTextfiles(source_directory)

    file_text = pgbookmarks.GetStartpageString(main_bc, 'templates')

    if not args.dry_run:
        pgbookmarks.WriteStartpageFile(file_text, output_directory)
        pgbookmarks.CopyStaticFiles(static_directory, output_directory)

        pgbookmarks.CreateDefaultFavicons(output_directory, main_bc)

        if args.download_favicons:
            pgbookmarks.DownloadFavicons(output_directory, main_bc)


if __name__ == '__main__':
    main()
