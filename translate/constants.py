LANGUAGES = {
    'af': 'Afrikaans',
    'sq': 'Shqip (Albanian)',
    'am': 'አማርኛ (Amharic)',
    'ar': 'العربية (Arabic)',
    'hy': 'Հայերեն (Armenian)',
    'az': 'Azərbaycan (Azerbaijani)',
    'eu': 'Euskara (Basque)',
    'be': 'Беларуская (Belarusian)',
    'bn': 'বাংলা (Bengali)',
    'bs': 'Bosanski (Bosnian)',
    'bg': 'Български (Bulgarian)',
    'ca': 'Català (Catalan)',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': '简体中文 (Chinese Simplified)',
    'zh-tw': '繁體中文 (Chinese Traditional)',
    'co': 'Corsu (Corsican)',
    'hr': 'Hrvatski (Croatian)',
    'cs': 'Čeština (Czech)',
    'da': 'Dansk (Danish)',
    'nl': 'Nederlands (Dutch)',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Eesti (Estonian)',
    'tl': 'Filipino',
    'fi': 'Suomi (Finnish)',
    'fr': 'Français (French)',
    'fy': 'Frysk (Frisian)',
    'gl': 'Galego (Galician)',
    'ka': 'ქართული (Georgian)',
    'de': 'Deutsch (German)',
    'el': 'Ελληνικά (Greek)',
    'gu': 'ગુજરાતી (Gujarati)',
    'ht': 'Kreyòl Ayisyen (Haitian Creole)',
    'ha': 'Hausa',
    'haw': 'ʻŌlelo Hawaiʻi (Hawaiian)',
    'iw': 'עברית (Hebrew)',
    'he': 'עברית (Hebrew)',
    'hi': 'हिन्दी (Hindi)',
    'hmn': 'Hmong',
    'hu': 'Magyar (Hungarian)',
    'is': 'Íslenska (Icelandic)',
    'ig': 'Igbo',
    'id': 'Bahasa Indonesia (Indonesian)',
    'ga': 'Gaeilge (Irish)',
    'it': 'Italiano (Italian)',
    'ja': '日本語 (Japanese)',
    'jw': 'Jawa (Javanese)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'kk': 'Қазақ (Kazakh)',
    'km': 'ភាសាខ្មែរ (Khmer)',
    'ko': '한국어 (Korean)',
    'ku': 'Kurdî (Kurdish)',
    'ky': 'Кыргызча (Kyrgyz)',
    'lo': 'ລາວ (Lao)',
    'la': 'Latina (Latin)',
    'lv': 'Latviešu (Latvian)',
    'lt': 'Lietuvių (Lithuanian)',
    'lb': 'Lëtzebuergesch (Luxembourgish)',
    'mk': 'Македонски (Macedonian)',
    'mg': 'Malagasy',
    'ms': 'Bahasa Melayu (Malay)',
    'ml': 'മലയാളം (Malayalam)',
    'mt': 'Malti (Maltese)',
    'mi': 'Te Reo Māori (Maori)',
    'mr': 'मराठी (Marathi)',
    'mn': 'Монгол (Mongolian)',
    'my': 'မြန်မာ (Burmese)',
    'ne': 'नेपाली (Nepali)',
    'no': 'Norsk (Norwegian)',
    'or': 'ଓଡ଼ିଆ (Odia)',
    'ps': 'پښتو (Pashto)',
    'fa': 'فارسی (Persian)',
    'pl': 'Polski (Polish)',
    'pt': 'Português (Portuguese)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)',
    'ro': 'Română (Romanian)',
    'ru': 'Русский (Russian)',
    'sm': 'Gagana Samoa (Samoan)',
    'gd': 'Gàidhlig (Scots Gaelic)',
    'sr': 'Српски (Serbian)',
    'st': 'Sesotho',
    'sn': 'ChiShona (Shona)',
    'sd': 'سنڌي (Sindhi)',
    'si': 'සිංහල (Sinhala)',
    'sk': 'Slovenčina (Slovak)',
    'sl': 'Slovenščina (Slovenian)',
    'so': 'Soomaali (Somali)',
    'es': 'Español (Spanish)',
    'su': 'Sunda',
    'sw': 'Kiswahili (Swahili)',
    'sv': 'Svenska (Swedish)',
    'tg': 'Тоҷикӣ (Tajik)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'th': 'ไทย (Thai)',
    'tr': 'Türkçe (Turkish)',
    'uk': 'Українська (Ukrainian)',
    'ur': 'اردو (Urdu)',
    'uz': 'Oʻzbekcha (Uzbek)',
    'vi': 'Tiếng Việt (Vietnamese)',
    'cy': 'Cymraeg (Welsh)',
    'xh': 'IsiXhosa',
    'yi': 'ייִדיש (Yiddish)',
    'zu': 'Zulu',
}

# ex. (("eng", "English"), ("es", "Español"), etc.)
TRANSLATE_CHOICES = (
    (lang_code, lang_title)
    for lang_code, lang_title in LANGUAGES.items()
)
