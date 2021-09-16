# azuretranslate
Python script using Azure Translator to detect and translate either typed phrase or document.

This script needs the following Python packages to be loaded :

pip install python-docx
pip install pypdf2
pip install python-magic

The script offers the option to enter a file location and file, or type a phrase to do initial language detection.

After the language has been detected, a selection of languages supported by the Translator API is displayed, along with the short code.

If the user wishes to translate their selection, type the short code for the desired language and the translated text will print
to the screen.
