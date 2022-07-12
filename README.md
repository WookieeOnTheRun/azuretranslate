# azuretranslate
Python script using Azure Translator to detect and translate either typed phrase or document. This script is built upon the Azure provided Quickstart.

This script needs the following Python packages to be loaded :

pip install python-docx

pip install pypdf2

pip install python-magic

You will also need to create an Azure Translator resource, and plug in the endpoint URL and key to use : https://docs.microsoft.com/en-us/azure/cognitive-services/translator/translator-how-to-signup

The script offers the option to either ingest a single demo file ( kafka.txt ) from a container in an Azure Blob Storage Account, or type a phrase to do initial language detection.

After the language has been detected, a selection of languages supported by the Translator API is displayed, along with the short code.

If the user wishes to translate their selection, type the short code for the desired language and the translated text will print
to the screen.

Source of demo text file : Project Gutenburg - text extracted
