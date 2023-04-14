import os
import json
import requests

from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from transformers import pipeline, AutoTokenizer, TFAutoModelForSeq2SeqLM

import pickle
import string
import tarfile
import gzip
from zipfile import ZipFile
import re


class EbookTranslate:
    def __init__(self, epub_path, language, use_api=False):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
        if use_api:
            self.tokenizer = None
            self.translation_api = f"http://my-translation-api.com/translate?from=en&to={language}"
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-en-es")
            self.model = TFAutoModelForSeq2SeqLM.from_pretrained(f"Helsinki-NLP/opus-mt-en-es")
            self.translation_api = None

    def filter_text(self, text):
        # Regular expression to match alphanumeric characters and spaces
        pattern = re.compile(r'[^\w\s]')
        # Replace everything else with an empty string
        filtered_text = pattern.sub('', text)
        # Split the filtered text into words
        words = filtered_text.split()
        # Join the words back into a string with spaces
        filtered_text = ' '.join(words)
        return filtered_text

    def _extract_text(self, section):
        if isinstance(section, epub.Section):
            for item in section.items:
                yield from self._extract_text(item)
        elif isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content.decode('utf-8'), 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            text = text.encode('ascii', 'ignore').decode()
            text = re.sub(r'\n\s*\n', '\n', text)
            yield self.filter_text(text)

    def _translate_text(self, text):
        if self.translation_api:
            r = requests.post(self.translation_api, data=json.dumps({'text': text}), headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                return r.json()['translation']
            else:
                raise ValueError(f"Translation API returned error code {r.status_code}")
        else:
            print(f"text: {text[:100]}")
            encoded_text = self.tokenizer.encode(text, return_tensors="tf")
            generated = self.model.generate(encoded_text)
            generated_text = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            return generated_text

    def _reinject_text(self, section, translated_text):
        if isinstance(section, epub.Section):
            for item in section.items:
                self._reinject_text(item, translated_text)
        elif isinstance(section, epub.EpubHtml):
            soup = BeautifulSoup(section.content, 'html.parser')
            new_content = ""
            for text in translated_text.split('\n'):
                new_content += f"<p>{text}</p>"
            soup.body.clear()
            soup.body.append(BeautifulSoup(new_content, 'html.parser'))
            section.content = str(soup)

    def translate_ebook(self):
        book_stop = 6
        i = 0
        for section in self.book.get_items():
            if i == 6 and section.get_type() == ebooklib.ITEM_DOCUMENT:
                text_chunks = [text_chunk.strip() for text_chunk in re.findall(r'\S.{0,510}\S(?=\s|$)|\S+', ''.join(self._extract_text(section)))]
                translated_text = []
                for chunk in text_chunks:
                    if len(chunk) <= 512:
                        print(f"chunk: {chunk[:100]}")
                        translated_text.append(self._translate_text(chunk))
                    else:
                        subchunks = [subchunk.strip() for subchunk in re.findall(r'\S.{0,508}\S(?=\s|$)|\S+', chunk)]
                        subchunk_translations = [self._translate_text(subchunk) for subchunk in subchunks]
                        translated_text.append(' '.join(subchunk_translations))
                print(translated_text)  # Add this line to see the contents of translated_text
                self._reinject_text(section, ' '.join(translated_text))

            i += 1
            if i > book_stop:
                break
        return self.book

    def get_translated_book_path(self):
        translated_ebook = self.translate_ebook()
        translated_epub_path = self.epub_path.replace(".epub", f"_translated.epub")
        epub.write_epub(translated_epub_path, translated_ebook)
        return translated_epub_path