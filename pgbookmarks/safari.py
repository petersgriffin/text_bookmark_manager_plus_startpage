import json
import logging
import subprocess

from .bookmarks import Bookmark_Collection, Bookmark_Folder, Bookmark

logger = logging.getLogger(__name__)


def LoadBookmarksFromSafari(bookmark_location):
    """ Safari bookmark file converted in place to JSOn; seems to be converted
    back to the binary format when used. Probably won't happen during execution
    """
    # assumes OSX utility plutil
    subprocess.Popen(['plutil', '-convert', 'json', bookmark_location, '-r'])

    bkms = Bookmark_Collection()

    safari_bookmarks = None
    with open(bookmark_location) as cf:
        safari_bookmarks = json.load(cf)
        logger.info(f"Loade Safari bookmarks file: {bookmark_location}")

    safari_bookmarks['Title'] = bkms.ROOT_NAME
    recursively_load_safari_children(bkms, safari_bookmarks, None)
    bkms.interconnect_children()

    return bkms


def recursively_load_safari_children(bkms, folder, parent_folder):
    if not parent_folder:
        bkms.folders[folder['Title']] = Bookmark_Folder(bkms.ROOT_NAME)
    else:
        bkms.folders[folder['Title']] = Bookmark_Folder(folder['Title'],
                                                        parent_folder['Title'])

    for child in folder['Children']:
        if 'Children' in child.keys():
            recursively_load_safari_children(bkms, child, folder)
        if 'URLString' in child.keys():
            bookmark = Bookmark(child['URIDictionary']['title'],
                                child['URLString'])
            logger.debug(bookmark)
            bkms.folders[folder['Title']].bookmarks.append(bookmark)
