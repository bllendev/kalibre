import os
import json
import requests

from bs4 import BeautifulSoup
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
    def __init__(self, epub_path, language, google_api=True, openai=False, fastapi=False):
        # key params
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)

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
        # google translate api
        if self.google_api:
            translator = Translator()
            return translator.translate(text, dest='es').text
        # openai not wired up yet... @AG++
        if self.translation_api:
            r = requests.post(self.translation_api, data=json.dumps({'text': text}), headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                return r.json()['translation']
            else:
                raise ValueError(f"Translation API returned error code {r.status_code}")
        # local huggingface transformer model
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
        for section in self.book.get_items():
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
        return self.book

    def get_translated_book_path(self):
        translated_ebook = self.translate_ebook()
        translated_epub_path = self.epub_path.replace(".epub", f"_translated.epub")
        epub.write_epub(translated_epub_path, translated_ebook)
        return translated_epub_path