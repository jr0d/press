import hashlib
import logging
import os
import requests
import time
import urlparse

from press.cli import run

log = logging.getLogger(__name__)


class Download(object):
    def __init__(self, url, hash_method=None, expected_hash=None, download_directory=None, filename=None,
                 chunk_size=20480, proxy=None):
        """A Download that also generates the checksum while downloading.

        Rarely will this clean be used directly.

        :param url: url of the file to Download
        :param hash_method: the actual hash algorithm used, sha1, md5, etc.
        :param expected_hash: expected hash of the file
        :param download_directory: directory to use to store the downloaded file
        :param filename: File name to store the download as, if None then it will be based on the original url, if
            that a name can't be determined, then a random name will be generated.
        :param chunk_size: how large of chunks to read from the stream.
        :param proxy: proxy server to use.
        """

        self.url = url
        self.hash_method = hash_method
        self.expected_hash = expected_hash
        self.download_directory = download_directory
        self.filename = filename
        self.chunk_size = chunk_size
        self.proxy = proxy
        self._hash = None

        if hash_method is not None:
            self.hash_method = hash_method.lower()
            self._hash = hashlib.new(self.hash_method)

        if expected_hash is not None:
            self.expected_hash = expected_hash.lower()

        if download_directory is None:
            self.download_directory = '/tmp'

        if filename is None:
            parsed_url = urlparse.urlparse(self.url)
            new_filename = os.path.basename(parsed_url.path)
            if new_filename:
                self.filename = new_filename
            else:
                self.filename = '%d.tmp' % time.time()

        self.full_filename = os.path.join(self.download_directory, self.filename)

    def __repr__(self):
        output = []
        for attr_name in ('url', 'hash_method', 'expected_hash', 'download_directory',
                          'filename', 'chunk_size'):
            attr = getattr(self, attr_name)
            output.append('%s=%s' % (attr_name, attr))
        return 'Download(%s)' % ', '.join(output)

    def download(self, callback_func):
        """Start the download_directory

        Downloads the file located at self.url to self.download_directory

        :param callback_func: expected signature is callback_func(total_downloaded)

        Raises an exception on error, otherwise the download was completed(as far as http is concerned)

        """
        byte_count = 0
        if self.proxy:
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        else:
            proxies = None

        ret = requests.get(self.url, stream=True, proxies=proxies)
        ret.raise_for_status()

        with open(self.full_filename, 'wb') as download_file:
            for chunk in ret.iter_content(self.chunk_size):
                byte_count += len(chunk)
                self._hash.update(chunk)
                download_file.write(chunk)
                callback_func(byte_count)

    def can_validate(self):
        """Can validate() actually work?

        Returns True if it is safe to call self.validate, otherwise False
        """
        return True if self.hash_method and self.expected_hash else False

    def validate(self):
        """Validate the checksum matches the expected checksum

        returns True if the checksum is matches expected_hash, otherwise False
        """
        return self._hash.hexdigest() == self.expected_hash

    def prepare_for_extract(self):
        """Prepare for extraction.

        This doesn't do anything, subclasses(like qcow) or something could do something like mount an image
        """
        pass

    def extract(self, target_path):
        """Extracts downloaded file to the target_path

        :param target_path: path to store extracted file in(must exist already)

        Returns an _AttributeString
        """

        # This is some ghetto crap to ensure that older versions of gnu-tar don't belly ache when it encounters a bz2.
        force_bzip_extensions = ('bz2', 'tbz', 'tbz2')
        compress_method = 'z'
        use_bzip = bool([i for i in force_bzip_extensions if self.filename.endswith(i)])
        if use_bzip:
            compress_method = 'j'
        return run('tar -C %s -%sxf %s' % (target_path, compress_method, self.full_filename))

    def cleanup(self):
        """Deletes downloaded file in this version
        """
        os.unlink(self.full_filename)


if __name__ == '__main__':

    def my_callback(bytes_so_far):
        print('Bytes so far: %d' % bytes_so_far)

    print('Starting download')
    dl = Download('http://cdimage.ubuntu.com/ubuntu-core/releases/trusty/release/ubuntu-core-14.04-core-amd64.tar.gz',
                  hash_method='sha1', expected_hash='ce3ad2ae205f5a90759d0a57b8cd90e687b4af1d', chunk_size=1024 * 1024)

    dl.download(my_callback)
    if dl.can_validate():
        print('Can do validation..')
        if dl.validate():
            print('Checksums match up!')
        else:
            print('Checksums do NOT MATCH!')
    else:
        print("Validation can't be performed")