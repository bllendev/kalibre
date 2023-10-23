# kalibre
**ebook management software**

**author**: Allen Garza

Hello! Welcome to Kalibre! This is a django web app which gives users a convenient place to send ebooks to whatever emails they please (including to straight to their kindles!). It will allow users to see a history of their previous book searches, a history of the books they've sent to themselves, and allows users to translate the books they send to themselves as they please. Kalibre uses several open repositories such as...
 - Libgen
 - OpenLibrary
 - ... with eventual support for...
 - Archvix
 - Project Gutenberg
 - Petrucci Music Library.

Kalibre is also a helpful AI Librarian, who can help users discern what they're looking for and help find and send the book or document they wish to send.

Visit here: https://kalibre-bllendev.herokuapp.com/

### Features
- 20+ langauge ebook translator
- AI librarian
- Manage and automate the processing and sending of nearly any public domain ebooks, emailing right to any e-reader

### Upcoming Features
- Kalibre Buddy - chrome extension to turn any web view into desired filetype, add to Kalibre account, email right to kindle (single button)
- Celery and asynchronous processing
- better mobile support
- kindle browser support (low js
- ... see active Milestones with **Feature:** tag

### How to run
- $ docker compose up --build -d

