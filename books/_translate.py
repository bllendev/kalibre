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
        except:
            # assume book is loaded
            self.epub_path = os.path.join(settings.BASE_DIR, f"{self.book.get_metadata('DC', 'title')[0][0]}")
            self.book = epub_path
        self.test_mode = test_mode  # NOTE: TEST IS SET TO TRUE FOR NOW... @AG++
        self._translate_count = 0

        # caching
        redis_url = os.environ.get("REDISCLOUD_URL", "redis://localhost:6379")
        if "local" in redis_url:
            self.redis = redis.StrictRedis(host='redis', port=6379, db=0)
        else:
            self.redis = redis.StrictRedis.from_url(redis_url)
        self.cached_used = 0

        # load models / apis
        self.fastapi = False
        self.openai = False
        self.google_api = False

        # fastapi model not finished yet... @AG++
        if fastapi:
            self.fastapi = True
            self.tokenizer = None
            self.translation_api = f"http://my-translation-api.com/translate?from=en&to={language}"
        # openai not wired up yet... @AG++
        elif openai:
            self.openai = True
            self.tokenizer = None
            self.translation_api = f"https://api.openai.com/v1/engines/davinci/completions"
        elif google_api:
            self.google_api = True
            self.tokenizer = None

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

    def _translate_and_cache(self, accumulated_chunks, translated_chunks):
        # Translate the accumulated chunks
        translated_accumulated = self._bulk_translate(accumulated_chunks)

        # Cache the translations and add them to the translated_chunks list
        for original, translated in zip(accumulated_chunks, translated_accumulated):
            normalized_text = self._normalize_text(original)
            self.redis.set(normalized_text, translated)
            translated_chunks.append(translated)

    def _bulk_translate(self, accumulated_chunks):
        # Combine accumulated chunks into a single string for translation
        text_to_translate = ' ||| '.join(accumulated_chunks)

        # Perform the translation (using your preferred API)
        translated_text = self._translate_single_text(text_to_translate)

        # Split the translated text back into individual chunks
        translated_chunks = translated_text.split(' ||| ')

        # Apply formatting to each translated chunk
        formatted_translated_chunks = [
            self._apply_formatting(original, translated)
            for original, translated in zip(accumulated_chunks, translated_chunks)
        ]

        return formatted_translated_chunks

    def _translate_single_text(self, text):
        # Implement the translation using your preferred API (Google Translate, OpenAI, etc.)
        # This is a placeholder implementation
        translator = Translator()
        translated_text = translator.translate(text, dest='es').text
        return translated_text

    def _group_and_translate(self, accumulated_texts):
        MAX_CHUNK_SIZE = 5000

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

        def get_translation_from_cache(text):
            normalized_text = self._normalize_text(text)
            cached_translation = self.redis.get(normalized_text)

            if cached_translation:
                self.cached_used += 1
                return self._apply_formatting(text, cached_translation.decode('utf-8'))
            return None

        def store_translation_in_cache(original_text, translated_text):
            normalized_text = self._normalize_text(original_text)
            self.redis.set(normalized_text, translated_text)

        grouped_texts = group_texts(accumulated_texts)
        translations = []

        for group in grouped_texts:
            translated_group = []

            for text in group:
                cached_translation = get_translation_from_cache(text)

                if cached_translation:
                    translated_group.append(cached_translation)
                else:
                    translated_group.append(None)

            non_cached_texts = [text for text in group if not get_translation_from_cache(text)]

            if non_cached_texts:
                non_cached_translations = self._bulk_translate(non_cached_texts)

                non_cached_index = 0
                for i, text in enumerate(group):
                    if translated_group[i] is None:
                        if non_cached_index < len(non_cached_translations):
                            translated_group[i] = non_cached_translations[non_cached_index]
                            store_translation_in_cache(text, non_cached_translations[non_cached_index])
                            non_cached_index += 1
                        else:
                            break

            translations.extend(translated_group)

        return grouped_texts, translations

    def _reinject_text(self, section):
        if isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')

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

            # Group and translate the accumulated_texts
            grouped_texts, translations = self._group_and_translate(accumulated_texts)

            # Replace text nodes with translations while preserving the original order
            for (parent, original_text_node), translation in zip(accumulated_nodes, translations):
                new_text_node = NavigableString(translation)
                original_text_node.replace_with(new_text_node)

                if self.test_mode:
                    print(f"Original: {str(original_text_node).strip()}")
                    print(f"Translated: {translation}")

            section.content = str(soup).encode('utf-8')

    def translate_ebook(self):
        """
        the primary function to 'translate' the ebook,
        translates text in place.

        params: **test_mode** (ctrl-f)
        """
        # test logs
        if self.test_mode:
            print("------------------- TEST CASE ------------------")
            print(f"Translating 1/4 of {self.book}...")
            i = 0
            i_test_threshold = len([item for item in self.book.get_items()]) / 4
            print(f"i_test_threshold: {i_test_threshold}")

        for section in self.book.get_items():
            if isinstance(section, epub.EpubHtml):
                # test threshold - allows for quicker testing
                if self.test_mode:
                    i += 1
                    if i > i_test_threshold:
                        break

                self._reinject_text(section)
        return self.book

    def get_translated_book_path(self, test=None):
        """
        the primary function to 'get' the translated book path
        ... - begins the translation process
        ... - writes the translated book to a new epub file
        params: test - boolean to indicate whether to run a test case
        ... test::True
        ... - 1/4 of the book will be translated & log stats to the console and file
        ... test::False then the entire book will be translated, and no logs
        """
        # set test
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

        return translated_epub_path