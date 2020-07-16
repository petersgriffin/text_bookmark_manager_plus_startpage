import os
import logging
import itertools

from urllib.parse import urlparse

logger = logging.getLogger(__name__)

COLUMNFILE_NAME = 'startpage.columns'


def LoadBookmarksFromTextfiles(textfile_root):
    """ external so filesystem loading is consistent with browser sources
    """
    bc = Bookmark_Collection()
    bc.loadBookmarksFromTextfiles(textfile_root)
    return bc


def GetBookmarkDiff(primary_bc, secondary_bc):
    """ Returns the bookmarks from a secondary Bookmark Collection (probably
    incidentally tracked in Chrome) not already tracked in the primary
    (probably the main textfile data).
    """
    primary = primary_bc.GetAllBookmarks()
    secondary = secondary_bc.GetAllBookmarks()

    difference = set(secondary) - set(primary)

    logger.debug(f'length of primary:      {len(primary)}')
    logger.debug(f'length of supplemental: {len(secondary)}')
    logger.debug(f'lenfth of difference:   {len(difference)}')

    return difference


def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if not domain or domain == '':
        return 'default'
    return domain


class Bookmark_Collection:
    """ Knows how to deal with the native filesystem format for import, export.
        Additional sources / export targets to be added outside the class.
    """

    ROOT_NAME = '/'

    def __init__(self):
        """ begins with a single, empty, root folder """
        self.folders = {}
        self.folders[self.ROOT_NAME] = Bookmark_Folder(self.ROOT_NAME)

        self.columns = []

    def GetAllBookmarks(self):
        lists = [folder.bookmarks for folder in self.folders.values()]
        return list(itertools.chain.from_iterable(lists))

    def GetAutocompletes(self):
        autocompletes = []

        for bookmark in self.GetAllBookmarks():

            parsed = urlparse(bookmark.link)
            candidate = bookmark.link
            scheme = parsed.scheme
            domain = parsed.hostname
            hard_url = bookmark.link

            if not domain:
                domain = ''
            autocompletes.append((bookmark.title, bookmark.link, '', domain))

            if scheme == 'http':
                candidate = bookmark.link[7:]
            elif scheme == 'https':
                candidate = bookmark.link[8:]
            else:
                logger.warning(f'Weird bookmark: {bookmark}')

            if parsed.path == '/':
                # for de-duping, removing trailing slashes for domain-bookmarks
                # without any query string
                hard_url = bookmark.link[:-1]
                candidate = candidate[:-1]

            autocompletes.append((candidate, hard_url, bookmark.title, domain))
            autocompletes.append((domain, f'{scheme}://{domain}', '', domain))

            if candidate.startswith('www.'):
                autocompletes.append((candidate[4:], hard_url, bookmark.title,
                                      domain))
                autocompletes.append((domain[4:], f'{scheme}://{domain}', '',
                                      domain))

        autocomplete_strings = []
        for autocom in sorted(set(autocompletes), key=lambda x: len(x[0])):
            # making a set to de-dupe, easier while as tuples than as dicts
            autocomplete_strings.append({"type_text": autocom[0],
                                         "url": autocom[1],
                                         "title": autocom[2],
                                         "domain": autocom[3]})
        # return '[' + (',').join(autocomplete_strings) + '];'
        return autocomplete_strings

    def GetAllDomains(self):
        return [bkm.domain for bkm in self.GetAllBookmarks()]

    def ExportToFilesystem(self, output_location):
        os.makedirs(output_location)

        for folder in self.folders.values():
            if folder.folder_id == self.ROOT_NAME:
                continue

            folder_path = os.path.join(output_location, f'{folder.folder_id}')
            if len(folder.children) > 0:
                os.makedirs(folder_path, exist_ok=True)
            if len(folder.bookmarks) > 0:
                file_path = os.path.join(output_location,
                                         f'{folder.folder_id}.txt')

                with open(file_path, 'w') as bookmark_file:
                    print((folder), file=bookmark_file)

    def loadBookmarksFromTextfiles(self, textfile_root):
        textfile_root = os.path.join(os.path.split(textfile_root)[0],
                                     os.path.split(textfile_root)[1])

        logger.debug(f'textfile_root: {textfile_root}')

        self.folders[self.ROOT_NAME] = Bookmark_Folder(self.ROOT_NAME)

        def recursively_load_subdirs(textfile_root, current_dir=None):
            logger.debug(f'current_dir: {current_dir}')
            if not current_dir:
                current_dir = textfile_root
            with os.scandir(current_dir) as dir_iterator:
                for path_item in dir_iterator:

                    current_path = os.path.relpath(path_item.path,
                                                   textfile_root)

                    folder_id = os.path.splitext(current_path)[0]

                    parent_path = os.path.relpath(current_dir, textfile_root)
                    if current_dir == textfile_root:
                        parent_path = self.ROOT_NAME

                    folder = None
                    if folder_id not in self.folders.keys():
                        folder = Bookmark_Folder(folder_id, parent_path)
                        self.folders[folder.folder_id] = folder
                    else:
                        folder = self.folders[folder_id]

                    if path_item.path.endswith('.txt') and path_item.is_file():
                        folder.loadTextFile(path_item.path)
                    if path_item.is_dir():
                        recursively_load_subdirs(textfile_root, path_item.path)

        recursively_load_subdirs(textfile_root)
        self.interconnect_children()

        columnsfile_path = os.path.join(textfile_root, COLUMNFILE_NAME)
        try:
            with open(columnsfile_path, 'r') as file:
                logger.info(f'Loading columns file {COLUMNFILE_NAME}')
                file_text = file.read().split('\n')
                for line in file_text:
                    if len(line.strip()) == 0:
                        continue
                    if line[0] == '#':
                        # line comments
                        continue
                    column = [c.strip() for c in line.split(',')]
                    self.columns.append(column)

            logger.debug(self.columns)

        except FileNotFoundError:
            logger.error(f'No columns file found at {columnsfile_path}!')
            logger.error('Defaulting to a single column!')
            self.columns.append(self.folders.values())

    def interconnect_children(self):
        for folder in self.folders.values():
            if not folder.parent_id:
                continue
            self.folders[folder.parent_id].children.append(folder.folder_id)

    def __str__(self):
        bkms_str = ""
        for folder in self.folders.values():
            if folder.folder_id == self.ROOT_NAME:
                continue

            if len(folder.bookmarks) > 0:
                file_str = folder.GetTextfileString()
                bkms_str += (f'\n{folder.folder_id}.txt:\n\n{file_str}')
        return bkms_str


class Bookmark_Folder:

    def __init__(self, folder_id, parent_id=None):
        self.folder_id = folder_id
        self.parent_id = parent_id

        self.title = self.folder_id

        self.bookmarks = []
        self.children = []

        logger.debug(f'folder_id: {self.folder_id}, title: {self.title}')

    def loadTextFile(self, textfile_location):
        """ Text files, and their directories, map directly to Bookmark_Folders
        """
        logger.info(f'textfile_location: {textfile_location}')
        with open(textfile_location, 'r') as f:
            file_text = f.read().split('\n')
            file_text.append('')  # sentinel value for files not ending with /n

            title = url = note = None
            for line in file_text:
                # building the bookmark sequentially, line-by-line
                logger.debug(line)
                if len(line) == 0:
                    # any number of blank lines separate bookmark entries
                    if len(line.strip()) > 0:
                        logger.warn(f'Separator line with whitespace: {line}')
                    if (title and not url) or (url and not title):
                        logger.error(f'Hanging title: {title} or url: {url}')
                    if title and url:
                        bookmark = Bookmark(title, url, note)
                        self.bookmarks.append(bookmark)
                    title = url = note = None
                    continue
                if not title:
                    title = line
                elif not url:
                    url = line
                elif not note:
                    note = line

    def __str__(self):
        return f"""str(Bookmark_Folder)
        folder_id:      {self.folder_id}
        title:          {self.title}
        parent_id:      {self.parent_id}
        children:       {self.children}
        len(bookmarks): {len(self.bookmarks)}"""

    def GetTextfileString(self):
        return '\n'.join([f'{b.GetTextfileString()}' for b in self.bookmarks])


class Bookmark:

    def __init__(self, title, link, note=None):
        self.title = title
        self.link = link
        self.note = note

        self.domain = get_domain(link)

    def GetTextfileString(self):
        if self.note:
            return f'{self.title}\n{self.link}\n{self.note}\n'
        return f'{self.title}\n{self.link}\n'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return f"""str(Bookmark):
        link:             {self.link}
        title:            {self.title}
        note:             {self.note}
        domain:           {self.domain}"""
