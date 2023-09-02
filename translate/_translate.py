from django.conf import settings
import itertools
import os
import json
import re
import requests
import time

import redis
from functools import lru_cache


from bs4 import BeautifulSoup, NavigableString
import ebooklib
from ebooklib import epub
from googletrans import Translator


class Translate:
    def __init__(self, fastapi=False, openai=False, google_api=True):
        # load models / apis
        self.fastapi = fastapi
        self.openai = openai
        self.google_api = google_api

        # fastapi model not finished yet... @AG++
        if self.fastapi:
            self.tokenizer = None
            self.translation_api = f"http://my-translation-api.com/translate?from=en&to={language}"
        # openai not wired up yet... @AG++
        elif self.openai:
            self.tokenizer = None
            self.translation_api = f"https://api.openai.com/v1/engines/davinci/completions"
        elif self.google_api:  # default
            self.google_translate = Translator()
            self.tokenizer = None

    def _google_translate_text(self, text, language):
        return self.google_translate.translate(text, dest=language).text

    def translate_text(self, text, language=""):
        if self.google_api:
            return self._google_translate_text(text, language)


class EbookTranslate:
    """
    EbookTranslate class for translating ebooks.

    - see Book._create_book_file() for usage.

    3 primary methods of translation intended for the following class...
    ... google_api - Google translate API
    ... openai - OpenAI API
    ... fastapi - homemade transformer model on fastapi infrastructure

    **test_mode*
    - param:test_mode - Boolean - if True, shortens tests to
    translating a 1/4 of the book, logs time, and cache results.
    """
    def __init__(self, epub_path, language, google_api=True, openai=False, fastapi=False, test_mode=True):
        # key params
        try:
            self.epub_path = epub_path
            self.book = epub.read_epub(epub_path)
        except Exception as e:
            # assume book is loaded
            self.epub_path = os.path.join(settings.BASE_DIR, f"{self.book.get_metadata('DC', 'title')[0][0]}")
            self.book = epub_path
            print(f"EbookTranslate - ERROR: {e}")

        # caching
        self.cached_used = 0
        if "development" in os.environ.get("ENVIRONMENT"):
            self.redis = redis.StrictRedis(host='redis', port=6379, db=0)
            self.test_mode = False  # NOTE: TEST IS SET TO TRUE FOR NOW ON LOCAL... @AG++
        else:
            redis_url = os.environ.get('REDISCLOUD_URL')
            self.redis = redis.StrictRedis.from_url(redis_url)
            self.test_mode = False

        # load models / apis
        self.translator = Translate(google_api=True, openai=False, fastapi=False)

        # debug
        self.translate_lang = language
        self.soup_strs = []
        self.accumulated_texts = []
        self.grouped_texts = []
        self.translations = []

    def _debug(self):
        """
        debug method for testing
        """
        if self.test_mode:
            # print(f"translate_lang: {self.translate_lang}")
            # print(f"accumulated_texts: {self.accumulated_texts}")
            # print(f"grouped_texts: {self.grouped_texts}")
            # print(f"translations: {self.translations}")

            # save json
            def save_as_json(data, filename):
                with open(os.path.join(settings.BASE_DIR, filename), 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

            save_as_json(self.accumulated_texts, 'accumulated_texts.json')
            save_as_json(self.grouped_texts, 'grouped_texts.json')
            save_as_json(self.translations, 'translations.json')
            save_as_json(self.soup_strs, 'soup_strs.json')

    def _normalize_text(self, text):
        """
        Normalize the text by lowercasing and removing punctuation.
        You can customize the normalization process as needed.

        param text: str - text to be normalized
        """
        normalized_text = text.lower()
        normalized_text = re.sub(r'[^\w\s]', '', normalized_text)
        return normalized_text

    def _apply_formatting(self, original_text, translated_text):
        """
        apply formatting from original text to translated text...
        - periods, commas, cases, spaces, etc.
        """
        original_words = original_text.split()
        translated_words = translated_text.split()
        formatted_words = []

        for orig_word, trans_word in itertools.zip_longest(original_words, translated_words):
            if orig_word is None:
                formatted_word = trans_word
            elif trans_word is None:
                continue
            elif orig_word[0].isupper():
                formatted_word = trans_word.capitalize()
            else:
                formatted_word = trans_word.lower()

            formatted_words.append(formatted_word)

        formatted_text = ' '.join(formatted_words)
        return formatted_text

    def _translate_single_text(self, text):
        """
        translate single text, accounts for xml tags
        """
        return self.translator.translate_text(text, self.translate_lang)

    def _bulk_translate(self, accumulated_chunks):
        """
        bulk translates text and applies formatting from the original text on each chunk
        """
        # filter out accumulated chunks that are tags
        filtered_accumulated_chunks = [
            text for text in accumulated_chunks
            if not text.startswith('<') and
            not text.startswith('xml') and
            not text.startswith('@page')
        ]

        # combine accumulated chunks into a single string for translation
        text_to_translate = ' ||| '.join(filtered_accumulated_chunks)

        # perform the translation (using your preferred API)
        translated_text = self._translate_single_text(text_to_translate)

        # split the translated text back into individual chunks
        translated_chunks = translated_text.split(' ||| ')

        # apply formatting to each translated chunk
        formatted_translated_chunks = [
            self._apply_formatting(original, translated)
            for original, translated in zip(filtered_accumulated_chunks, translated_chunks)
        ]

        return formatted_translated_chunks

    def _group_and_translate(self, accumulated_texts):
        """
        this method accepts a list of accumulated_texts and returns them grouped into chunks of a maximum size
        and their respective translations. The method also uses caching mechanism to store and retrieve translations
        to/from Redis.

        parameters:
        ----------
        accumulated_texts : list
            The list of strings to be grouped and translated.

        returns:
        -------
        tuple
            A tuple of two lists. The first list contains the grouped texts and the second one contains
            the respective translations of these groups.

        notes:
        ------
        - texts are grouped using the MAX_CHUNK_SIZE constant, which is currently set to 5000.
        - a text is appended to the current group as long as it doesn't exceed the MAX_CHUNK_SIZE when added.
        - each text is checked against the cache before being translated. If a translation is available in the cache
        it is used, otherwise, it's marked as None.
        - non-cached texts are bulk translated, and their translations are stored in the cache for future use.
        """
        MAX_CHUNK_SIZE = 5000

        # helper method - group texts into chunks of a maximum size
        def group_texts(text_list):
            grouped_texts = []
            current_group = []
            current_length = 0

            for text in text_list:
                text_length = len(text)

                if current_length + text_length + 3 > MAX_CHUNK_SIZE:
                    grouped_texts.append(current_group)
                    current_group = []
                    current_length = 0

                current_group.append(text)
                current_length += text_length + 3

            if current_group:
                grouped_texts.append(current_group)

            return grouped_texts

        # helper method - get translation from cache
        def get_translation_from_cache(text):
            normalized_text = self._normalize_text(text)
            cached_translation = self.redis.get(normalized_text)

            if cached_translation:
                self.cached_used += 1
                return self._apply_formatting(text, cached_translation.decode('utf-8'))
            return None

        # helper method - store translation in cache
        def store_translation_in_cache(original_text, translated_text):
            normalized_text = self._normalize_text(original_text)
            self.redis.set(normalized_text, translated_text)

        # group texts into chunks of a maximum size
        grouped_texts = group_texts(accumulated_texts)
        grouped_texts_translations = []
        for group in grouped_texts:

            # get cached translation groups, set None for non-cached texts
            translated_group = []
            for text in group:
                cached_translation = get_translation_from_cache(text)

                # true - append ached_translation
                if cached_translation:
                    translated_group.append(cached_translation)

                # false = mark non-cached texts as None
                else:
                    translated_group.append(None)

            # translate non-cached texts
            non_cached_texts = [text for text in group if not get_translation_from_cache(text)]
            if non_cached_texts:
                non_cached_translations = self._bulk_translate(non_cached_texts)

                # inject into translated_group where None - cache translations
                non_cached_index = 0
                for i, text in enumerate(group):
                    if translated_group[i] is None:
                        if non_cached_index < len(non_cached_translations):
                            # inject translated text into translated_group
                            translated_group[i] = non_cached_translations[non_cached_index]

                            # store translated text in cache
                            store_translation_in_cache(text, non_cached_translations[non_cached_index])

                            # increment non_cached_index
                            non_cached_index += 1
                        else:
                            break

            grouped_texts_translations.extend(translated_group)

        return grouped_texts, grouped_texts_translations

    def _reinject_text(self, section):
        """
        this method handles sections of type epub.EpubHtml by performing the following steps:

        1. retrieve the parsed HTML content (soup) of the section using the helper function `get_section_soup`.

        2. define a helper function, `collect_text_nodes`, which is used to recursively collect all text nodes from the parse tree. A text node is a NavigableString which is not empty after being stripped. Both the parent node and the text node are kept for each text node found.

        3. collect all text nodes using the `collect_text_nodes` function.

        4. accumulate both the nodes and the stripped texts in separate lists for further processing.

        5. group and translate the accumulated texts using the `_group_and_translate` method.

        6. replace the original text nodes in the parse tree with their translated counterparts while preserving their original order. If a text node matches a specific string or if the program is running in test_mode, additional debugging information is printed out.

        7. encode the updated parse tree back into bytes using the original encoding and save it back to the section content.

        :param section: epub.EpubHtml - Section of the ebook to be processed...
        .. NOTE: that this function modifies the section content in-place...
        ... The original text nodes in the section content are replaced by their translated counterparts.

        :return: None - The section content is modified in-place.
        """
        soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')

        self.soup_strs.append(str(soup))

        def collect_text_nodes(node, text_nodes):
            if not hasattr(node, 'contents') or not node.contents:
                return

            for child in node.contents:
                if isinstance(child, NavigableString):
                    original_text = str(child).strip()
                    if original_text:
                        text_nodes.append((child.parent, child))
                else:
                    collect_text_nodes(child, text_nodes)

        text_nodes = []
        collect_text_nodes(soup, text_nodes)

        accumulated_nodes = []
        accumulated_texts = []

        for parent, original_text_node in text_nodes:
            original_text = str(original_text_node).strip()
            accumulated_nodes.append((parent, original_text_node))
            accumulated_texts.append(original_text)

            # test_mode
            if self.test_mode:
                self.accumulated_texts.append(accumulated_texts)

        # group and translate the accumulated_texts
        grouped_texts, translations = self._group_and_translate(accumulated_texts)

        # test_mode
        if self.test_mode:
            self.grouped_texts.append(grouped_texts)
            self.translations.append(translations)

        # replace text nodes with translations while preserving the original order
        for (parent, original_text_node), translation in zip(accumulated_nodes, translations):
            if translation:
                new_text_node = NavigableString(translation)
                original_text_node.replace_with(new_text_node)

                # test_mode
                if self.test_mode:
                    pass
                    # print(f"Original: {str(original_text_node).strip()}")
                    # print(f"Translated: {translation}")

        # encode the content back into bytes using the original encoding
        section.content = str(soup).encode('utf-8')

    def translate_ebook(self):
        """
        the primary function to 'translate' the ebook,
        translates text in place (replaces text of original file).

        params: **test_mode** (ctrl-f)

        returns: translated book
        """
        # test_mode
        if self.test_mode:
            print("------------------- TEST CASE ------------------")
            print(f"Translating 1/4 of {self.book}...")
            i = 0
            i_test_threshold = len([item for item in self.book.get_items()]) / 4
            print(f"i_test_threshold: {i_test_threshold}")

        for section in self.book.get_items():
            print(f"type: {epub.EpubItem.get_type(section)}")

            if isinstance(section, (epub.EpubHtml)):  # handle other item types

                # reinject translated text by section
                self._reinject_text(section)

                # test_mode - allows for quicker testing
                if self.test_mode:
                    i += 1
                    if i > i_test_threshold:
                        break

            else:
                if self.test_mode:
                    print(f"EbookTranslate.translate_ebook: section is not of type epub.EpubHtml - {section} - {i}")

        return self.book

    def get_translated_book_path(self, test=None):
        """
        the primary function to 'get' the translated book path
        ... - begins the translation process
        ... - writes the translated book to a new epub file

        params: test - boolean to indicate whether to run a test case
        ... test::True - 1/4 of the book will be translated & log stats to the console and file
        ... test::False - entire book will be translated, and no logs

        returns: translated_epub_path - the path to the translated epub file
        """
        # set test_mode
        test = self.test_mode if test is None else test
        if test:
            self.test_mode = True
            print(f"Translating {self.epub_path}... logging time...")

        # translate the ebook (time)
        start_time = time.time()
        translated_ebook = self.translate_ebook()
        end_time = time.time()

        # save translated ebook
        translated_epub_path = self.epub_path.replace(".epub", f"_translated.epub")
        epub.write_epub(translated_epub_path, translated_ebook)

        # log stats (testing purposes)
        if self.test_mode:
            # prepare the stats
            cache_stat = f"self.cached_used: {self.cached_used}"
            time_stat = f"time of translation: {end_time - start_time}"

            # print the stats
            print(cache_stat)
            print(time_stat)

            # create a unique filename using the epub_path
            filename = re.sub(r'\W+', '_', os.path.splitext(os.path.basename(translated_epub_path))[0])
            filename = f"stats_{filename}.txt"

            # save the stats to the uniquely named text file
            with open(filename, "w") as f:
                f.write(f"{cache_stat}\n{time_stat}\n")

        # test_mode
        self._debug()

        # return
        return translated_epub_path
