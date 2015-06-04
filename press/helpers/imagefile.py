import hashlib
import logging
import os
import requests
import shutil
import time
import urlparse

from press.helpers.deployment import tar_extract


log = logging.getLogger(__name__)


class ImageFile(object):
    def __init__(self, url, target, hash_method=None, expected_hash=None, download_directory=None,
                 filename=None, buffer_size=20480, proxy=None):
        """
        Extending (or renaming really) Chad Catlett's Download class.

        Image download, detection (tar?,cpio?,qcow?), validation, extraction, and cleanup operations.

        :param url: extended url format, supporting http://,https://,file:// <and more?>
        :param target: a top-level directory where we extract/copy image files to
        :param hash_method: sha1, md5, sha256 or None
        :param expected_hash: pre-recorded hash
        :param download_directory: where to place the temporary file
        :param filename: the name of the temporary file
        :param buffer_size: maximum size of buffer for stream operations
        :param proxy: a proxy server in host:port format
        """

        self.url = url
        self.hash_method = hash_method
        self.expected_hash = expected_hash
        self.download_directory = download_directory
        self.filename = filename
        self.buffer_size = buffer_size
        self.proxy = proxy
        self._hash_object = None

        if hash_method:
            self.hash_method = hash_method.lower()
            self._hash_object = hashlib.new(self.hash_method)

        if download_directory is None:
            self.download_directory = '/tmp'

        parsed_url = urlparse.urlparse(self.url)

        self.url_scheme = parsed_url.scheme

        if not filename:
            new_filename = os.path.basename(parsed_url.path)
            if not new_filename:
                self.filename = new_filename
            else:
                self.filename = '%d.tmp' % time.time()

        self.full_filename = os.path.join(self.download_directory, self.filename)

    def hash_file(self):
        """
        If we are not downloading the file, we still need to hash it
        :return:
        """
        with open(self.full_filename, 'rb') as fp:
            while True:
                data = fp.read(self.buffer_size)
                if not data:
                    break
                self._hash_object.update(data)

    def downlaod(self):
