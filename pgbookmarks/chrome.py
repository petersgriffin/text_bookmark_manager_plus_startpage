import json
import logging
from .bookmarks import Bookmark_Collection, Bookmark_Folder, Bookmark

logger = logging.getLogger(__name__)


def LoadBookmarksFromChrome(bookmark_location):

    bkms = Bookmark_Collection()

    chrome_bookmarks = None
    with open(bookmark_location) as cf:
        chrome_bookmarks = json.load(cf)
        logger.info(f"Loaded Chrome bookmarks file: {bookmark_location}")

    # 'other bookmarks', 'mobile' are ignored; I haven't used them.
    data = chrome_bookmarks['roots']['bookmark_bar']
    data['name'] = bkms.ROOT_NAME
    recursively_load_chrome_children(bkms, data, None)
    bkms.interconnect_children()

    return bkms


def recursively_load_chrome_children(bkms, folder, parent_folder):
    if not parent_folder:
        bkms.folders[folder['name']] = Bookmark_Folder(bkms.ROOT_NAME)
    else:
        bkms.folders[folder['name']] = Bookmark_Folder(folder['name'],
                                                       parent_folder['name'])

    for child in folder['children']:
        if 'children' in child.keys():
            recursively_load_chrome_children(bkms, child, folder)
        if 'url' in child.keys():
            bookmark = Bookmark(child['name'], child['url'])
            logger.debug(bookmark)
            bkms.folders[folder['name']].bookmarks.append(bookmark)
