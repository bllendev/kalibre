import os

from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

import pickle
import string
import tarfile
import gzip
from zipfile import ZipFile


class EbookTranslate():

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def __init__(self, epub_path):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
