from django.conf import settings


TEST_QUERY = "my sweet orange tree"

TEST_ISBN = "2670677"       # my sweet orange tree

TEST_BOOK_FILETYPE = "epub"

TEST_COLUMNS = [
    "ID",
    "Author",
    "Title",
    "Publisher",
    "Year",
    "Pages",
    "Language",
    "Size",
    "Extension",
    "Mirror_1",
    "Mirror_2",
    "Mirror_3",
    "Mirror_4",
    "Mirror_5",
    "Edit",
]

TEST_LIBGEN_MIRRORS = [
    "https://libgen.is",
    "http://libgen.gs",
    "http://gen.lib.rus.ec",
    "http://libgen.rs",
    "https://libgen.st",
    "https://libgen.li",
]

TEST_EMAIL_TEMPLATE_LIST = [
    '',                                         # empty subject line
    '',                                         # empty message line
    str(settings.DEFAULT_FROM_EMAIL),           # from email
    list(),                                     # recipient_list
]

TEST_STABLE_FILE_TYPES = {"epub", "mobi"}