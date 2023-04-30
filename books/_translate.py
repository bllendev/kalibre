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
# from transformers import pipeline, AutoTokenizer, TFAutoModelForSeq2SeqLM  # not in Pipfile


class EbookTranslate:
    """
    4 primary methods of translation intended for the following class...
    ... google_api - Google translate API
    ... openai - OpenAI API
    ... fastapi - homemade transformer model on fastapi infrastructure
    ... else - local huggingface transformer model
    """
    def __init__(self, epub_path, language, google_api=True, openai=False, fastapi=False, test=True):
        # key params
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
        self.test = test  # NOTE: TEST IS SET TO TRUE FOR NOW... @AG++

        # caching
        redis_url = os.environ.get("REDISCLOUD_URL", "redis://localhost:6379")
        self.redis = redis.StrictRedis(host='redis', port=6379, db=0)

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
        # using my version of google translate api... @AG++
        elif google_api:
            self.google_api = True
            self.tokenizer = None

    def filter_text(self, text):
        return text.strip()
        # # Regular expression to match alphanumeric characters and spaces
        # pattern = re.compile(r'[^\w\s]')
        # # Replace everything else with an empty string
        # filtered_text = pattern.sub('', text)
        # # Split the filtered text into words
        # words = filtered_text.split()
        # # Join the words back into a string with spaces
        # filtered_text = ' '.join(words)
        # return filtered_text

    def _extract_text(self, section):
        if isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()

            texts = []
            for text_node in soup.stripped_strings:
                filtered_text = self.filter_text(text_node)
                text_node_bs = NavigableString(filtered_text)
                texts.append((text_node, text_node_bs))  # Save the text_node and its NavigableString counterpart

            return texts
        return []  # Return an empty list for non-EpubHtml sections

    def _normalize_text(self, text):
        # Normalize the text by lowercasing and removing punctuation.
        # You can customize the normalization process as needed.
        normalized_text = text.lower()
        normalized_text = re.sub(r'[^\w\s]', '', normalized_text)
        return normalized_text

    def _apply_formatting(self, original_text, translated_text):
        # Apply the original formatting (punctuation, case-size) to the translated text
        # This is a simple example, you may need to create a more sophisticated function
        formatted_text = ""
        for orig_char, trans_char in zip(original_text, translated_text):
            if orig_char.isupper():
                formatted_text += trans_char.upper()
            else:
                formatted_text += trans_char

        return formatted_text

    def _translate_text(self, text):
        if "xml version" in text:
            return ""  # skip XML declarations (don't expose in text)

        # Check the Redis cache for a translation
        normalized_text = self._normalize_text(text)
        translated_text = self.redis.get(normalized_text)
        if translated_text:
            self.cached_used += 1
            translated_text = self._apply_formatting(text, translated_text.decode('utf-8'))
            return translated_text

        # google translate api
        if self.google_api:
            translator = Translator()
            translated_text = translator.translate(text, dest='es').text

        # openai not wired up yet... @AG++
        elif self.translation_api:
            r = requests.post(self.translation_api, data=json.dumps({'text': text}), headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                translate_text = r.json()['translation']
            else:
                raise ValueError(f"Translation API returned error code {r.status_code}")

        # local huggingface transformer model
        else:
            encoded_text = self.tokenizer.encode(text, return_tensors="tf")
            generated = self.model.generate(encoded_text)
            translated_text = self.tokenizer.decode(generated[0], skip_special_tokens=True)

        # Cache the translation in Redis
        self.redis.set(text, translated_text)
        return translated_text

    def _reinject_text(self, section):
        if isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')

            # helper function to traverse the tree, collect NavigableStrings and their parents
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

            # translate and replace text
            for parent, original_text_node in text_nodes:
                original_text = str(original_text_node).strip()
                translated_text = self._translate_text(original_text)
                new_text_node = NavigableString(translated_text)
                original_text_node.replace_with(new_text_node)

                if self.test:
                    print(f"Original: {original_text}")
                    print(f"Translated: {translated_text}")

            # update the section content with the modified soup
            section.content = str(soup).encode('utf-8')

    def translate_ebook(self):
        """
        the primary function to 'translate' the ebook,
        translates text in place.
        """
        if self.test:
            print("------------------- TEST CASE ------------------")
            print(f"Translating 1/4 of {self.book}...")
            i = 0
            i_test_threshold = len([item for item in self.book.get_items()]) / 4
            print(f"i_test_threshold: {i_test_threshold}")

        for section in self.book.get_items():
            if isinstance(section, epub.EpubHtml):
                # test threshold - allows for quicker testing
                if self.test:
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
        test = self.test if test is None else test
        if test:
            self.test = True
            print(f"Translating {self.epub_path}... logging time...")

        start_time = time.time()
        translated_ebook = self.translate_ebook()
        end_time = time.time()

        translated_epub_path = self.epub_path.replace(".epub", f"_translated.epub")
        epub.write_epub(translated_epub_path, translated_ebook)

        if self.test:
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