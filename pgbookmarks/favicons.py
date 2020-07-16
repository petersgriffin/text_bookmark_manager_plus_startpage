import os
import threading
import requests

from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.parse import urljoin

import logging
import time
import shutil

from .bookmarks import get_domain


logger = logging.getLogger(__name__)


def favicon_path(output_directory, domain):
    return os.path.join(output_directory, 'favicons', domain, 'favicon.png')


def downloaded_favicon_path(output_directory, domain):
    return os.path.join(output_directory, 'favicons', domain, 'download.png')


def download_favicon(output_directory, domain, icon_url):
    download_path = downloaded_favicon_path(output_directory, domain)

    try:
        r = requests.get(icon_url, stream=True, timeout=8)

        if not r.status_code == 200:
            logger.warn(f'{domain}: HTTP {r.status_code} for {icon_url}')
            logger.debug(r)

        logger.info(f'Downloading: {domain}, {icon_url} to: {download_path}')
        with open(download_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        shutil.copy(download_path, favicon_path(output_directory, domain))

    except requests.exceptions.ConnectionError as e:
        logger.error(f'Error connecting to: {domain}, error: {e}')


def get_remote_favicon_url(domain):
    logger.debug(f'Getting homepage for: {domain}')

    url = f"https://{domain}"
    body = None

    try:
        r = requests.get(url, stream=True, timeout=8)
        if hasattr(r, 'location'):
            if get_domain(r.location) == domain:
                # only follow 1 redirect to same domain, mainly for HTTPS
                url = r.location
                r = requests.get(r.location, stream=True, timeout=8)

        if r.status_code != 200:
            logger.warn(f'{domain}: HTTP {r.status_code} for {url}')
            logger.debug(r)

        body = r.text
    except requests.exceptions.ConnectionError as e:
        logger.error(f'Error connecting to: {domain}, error: {e}')
        return None
    except requests.exceptions.ReadTimeout as e:
        logger.error(f'HTTP read timeout for: {domain}, error: {e}')
        return None

    soup = BeautifulSoup(body, 'html.parser')
    for link in soup.find_all('link'):
        if any(xx in link['rel'] for xx in ['icon', 'Icon', 'ICON']):

            icon_url = link['href']
            parsed_icon_url = urlparse(icon_url)

            if parsed_icon_url.scheme not in ['https', 'http']:
                icon_url = urljoin(url, parsed_icon_url.path)
                logger.debug(f"Relative icon, prepending as {icon_url}")

            # ASSUMPTION: first icon link in the BS4-parsed list is the best
            return icon_url


def favicon_download_worker(output_directory, domain_list):
    while len(domain_list) > 0:
        domain = domain_list.pop()

        if os.path.exists(downloaded_favicon_path(output_directory, domain)):
            logger.info(f'Downloaded favicon exists, skipping DL for {domain}')
            continue

        # courtesy time between two requests to possibly the same IP
        time.sleep(1)

        icon_url = get_remote_favicon_url(domain)
        if not icon_url:
            logger.warn(f"No Favicon acquired from {domain}")
            continue

        download_favicon(output_directory, domain, icon_url)


def CreateDefaultFavicons(output_directory, bookmark_collection):
    domains = [bkm.domain for bkm in bookmark_collection.GetAllBookmarks()]
    domains = sorted(set(domains))

    for domain in domains:
        domain_dir = os.path.join(output_directory, 'favicons', domain)
        os.makedirs(domain_dir, exist_ok=True)
        shutil.copyfile(os.path.join(output_directory, 'default_favicon.png'),
                        os.path.join(domain_dir, 'favicon.png'))

        if os.path.exists(os.path.join(domain_dir, 'download.png')):
            shutil.copyfile(os.path.join(domain_dir, 'download.png'),
                            os.path.join(domain_dir, 'favicon.png'))


def DownloadFavicons(output_directory, bookmark_collection):
    domains = [bkm.domain for bkm in bookmark_collection.GetAllBookmarks()]
    domains = sorted(set(domains))

    threads = []
    for i in range(1):
        t = threading.Thread(target=favicon_download_worker,
                             args=(output_directory, domains,))
        threads.append(t)
        t.start()
