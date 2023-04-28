import os
import json
import requests

from bs4 import BeautifulSoup, NavigableString
import ebooklib
from ebooklib import epub
from googletrans import Translator
# from transformers import pipeline, AutoTokenizer, TFAutoModelForSeq2SeqLM

import re


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
        self.test = test
        self.translation_cache = {}
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

    def _translate_text(self, text):
        if "xml version" in text:
            return ""  # skip XML declarations (don't expose in text)

        if text in self.translation_cache:
            self.cached_used += 1
            return self.translation_cache[text]

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

        # Cache the translation
        self.translation_cache[text] = translated_text
        return translated_text

    def _reinject_text(self, section):
        if isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')

            # Helper function to traverse the tree, collect NavigableStrings and their parents
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

            # Translate and replace text
            for parent, original_text_node in text_nodes:
                original_text = str(original_text_node).strip()
                translated_text = self._translate_text(original_text)
                new_text_node = NavigableString(translated_text)
                original_text_node.replace_with(new_text_node)

                if self.test:
                    print(f"Original: {original_text}")
                    print(f"Translated: {translated_text}")

            # Update the section content with the modified soup
            section.content = str(soup).encode('utf-8')

    def translate_ebook(self):
        if self.test:
            print("---------- TEST CASE --------")
            print(f"Translating 1/5 of {self.book}...")
            i = 0
            i_test_threshold = len([item for item in self.book.get_items()]) / 6
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

    def get_translated_book_path(self):
        translated_ebook = self.translate_ebook()
        translated_epub_path = self.epub_path.replace(".epub", f"_translated.epub")
        epub.write_epub(translated_epub_path, translated_ebook)
        print(f"self.cached_used: {self.cached_used}")
        return translated_epub_path