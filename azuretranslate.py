import requests
import uuid
import json

# import packages for document format(s)
import magic # detects file format
from PyPDF2 import pdf # allows loading/reading of PDF files
import docx # allows reading of MS Word files

# Add your region, subscription key and endpoint
# Region is required if using a Cognitive Services resource.

subscription_key = ""
endpoint = ""

translatePath = '/translate?api-version=3.0'
detectPath = '/detect?api-version=3.0'
languagePath = '/languages?api-version=3.0&scope=translation'

# list of characters to strip from content strings
charList = [ "\t", "\n", "\r", "\v", "\f" ]

# add logic to either translate/detect a single phrase or the contents of a document

docOrPhrase = input( "Would you like to work with an existing document or enter a phrase? Enter 0 for document or 1 for phrase : " )

if docOrPhrase == "0" :

	docLocation = input( "Please enter the location and name of the document - currently this script only supports text, MS Word ( Docx ) and PDF : " )

	fileType = magic.from_file( docLocation, mime = True )

	print( "File Type : ", fileType )

	if fileType == "application/pdf" :

		# use PyPDF2

		docText = ""

		pdfToProcess = open( docLocation, "rb" )

		pdfReader = pdf.PdfFileReader( pdfToProcess )

		currPage = 0

		# print( "Num Pages : ", pdfReader.numPages )

		while currPage <= ( ( pdfReader.numPages ) - 1 ) :

			pdfPage = pdfReader.getPage( currPage )

			pdfText = pdfPage.extractText()

			docText += pdfText

			currPage += 1

			# print( docText )

			for char in charList :

				docText = docText.replace( char, "" )

		workBlock = '[{ "text" : "' + docText + '" }]'

		pdfToProcess.close()

	elif fileType == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" :

		# use docx

		docToProcess = open( docLocation, "rb" )

		docReader = docx.Document( docToProcess )

		docText = ""

		for para in docReader.paragraphs :

			docText += para.text

			for char in charList :

				docText = docText.replace( char, "" )
			
		# print( docText )

		workBlock = '[{ "text" : "' + docText + '" }]'

		docToProcess.close()

	else :

		docToProcess = open( docLocation, "r" )

		docText = docToProcess.read()

		for char in charList :

			docText = docText.replace( char, "" )

			workBlock = '[{ "text" : "' + docText + '" }]'

		docToProcess.close()

elif docOrPhrase == "1" :

	phraseToProcess = input( "Please enter a phrase you want to process : " )

	workBlock = '[{ "text" : "' + phraseToProcess + '" }]'

phrase = json.loads( workBlock )

headers = {
	'Ocp-Apim-Subscription-Key': subscription_key,
	'Ocp-apim-subscription-region' : 'usgovvirginia',
	'Content-type': 'application/json',		
	'X-ClientTraceId': str(uuid.uuid4())
	}

body = phrase

# get list of supported languages for translation
constructed_url = endpoint + languagePath

# print( constructed_url )
# print( tmpHeaders )

# request = requests.post( constructed_url , headers = tmpHeaders, json = body )
request = requests.get( constructed_url )
response = request.json()

jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False )
languageDict = json.loads( jsonString )

# print( type( languageDict ) )
# print( len( languageDict ) )

# detecting language by default - option offered to translate into supported language
constructed_url = endpoint + detectPath

request = requests.post( constructed_url, headers = headers, json = body )
response = request.json()

jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ' ) )
detectJsonObj = json.loads( jsonString )

detectedLanguage = detectJsonObj[ 0 ][ "language" ]

displayLanguage = languageDict[ "translation" ][ detectedLanguage ][ "name" ]

toTranslate = input( "We have detected the language as " + displayLanguage + " - would you like to translate? Please enter Y or Yes to translate, N or No to end with detection : " )

if toTranslate.upper() == "Y" or toTranslate.upper() == "YES" :

	print( "Please select a language to translate into from the list below: " )

	for key, value in languageDict[ "translation" ].items() :

		print( "Available languages : ", key, " - ", languageDict[ "translation" ][ key ][ "name" ] )

	desiredLanguage = input( "Please type short code for desired translation language : " )

	if desiredLanguage in languageDict[ "translation" ] :

		# params = "&from=en&to=es&to=fr&to=de&to=it"
		params = "&from=" + detectedLanguage + "&to=" + desiredLanguage

		constructed_url = endpoint + translatePath + params

		request = requests.post( constructed_url, headers = headers, json = body )
		response = request.json()

		# print( json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ' ) ) )
		jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ' ) )
		translateJsonObj = json.loads( jsonString )

		# translatedText = translateJsonObj[ 0 ][ 0 ]
		translatedText = translateJsonObj[ 0 ][ 0 ][ 0 ]

		print( "Translated Text :" )
		print( translatedText )

	else :

		print( "Invalid language code selected." )

else :

	print( "All done." )