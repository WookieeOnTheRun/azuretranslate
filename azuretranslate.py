import requests
import uuid
import json

# import packages for document format(s)
import magic # detects file format
from PyPDF2 import pdf # allows loading/reading of PDF files
import docx
from requests.api import head
from requests.models import Response # allows reading of MS Word files

# Add your region, subscription key and endpoint
# Region is required if using a Cognitive Services resource.

subscription_key = ""
endpoint = ""

translatePath = '/translate?api-version=3.0'
detectPath = '/detect?api-version=3.0'
languagePath = '/languages?api-version=3.0&scope=translation'

headers = {
	'Ocp-Apim-Subscription-Key': subscription_key,
	'Ocp-apim-subscription-region' : 'usgovvirginia',
	'Content-type': 'application/json',		
	'X-ClientTraceId': str(uuid.uuid4())
	}

###############################################################################
# function - convert passed document to json block for use by translation api #
###############################################################################

def ConvertDocToJson( rawFile, rawFormat ) :

    charList = [ "\t", "\n", "\r", "\v", "\f" ]

    jsonBlock = ""

    docText = ""

    if rawFormat == "application/pdf" :

        # pdf

        docToProcess = open( rawFile, "rb" )

        docReader = pdf.PdfFileReader( docToProcess )

        currPage = 0

        while currPage <= ( ( docReader.numPages ) -1 ) :

            docPage = docReader.getPage( currPage )

            currText = docPage.extractText()

            docText += currText

            currPage += 1

    elif rawFormat == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" :

        # word doc

        docToProcess = open( rawFile, "rb" )

        docReader = docx.Document( docToProcess )

        docToProcess.close()

        for para in docReader.paragraphs :

            docText += para.text

    else :

        docToProcess = open( rawFile, "r" )

        docText = docToProcess.read()

        docToProcess.close()

    for char in charList :

        docText = docText.replace( char, "" )

    jsonBlock = '[{ "text" : "' + docText + '" }]'

    workBlock = json.loads( jsonBlock )

    return workBlock;

################################################
# function - displayed API supported languages #
################################################

def getSupportedLanguages( epUrl, langPath ) :

    endpoint = epUrl + langPath

    # print( endpoint )

    request = requests.get( endpoint )

    response = request.json()

    jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False )

    jsonLangObj = json.loads( jsonString )

    global detectedLanguages

    detectedLanguages = jsonLangObj[ "translation" ]

    # print( detectedLanguages )

    return detectedLanguages

##############################################
# function : detect json block with api call #
##############################################

def detectJsonBlock( jsonBlock, epUrl, detectPath, langPath ) :

    urlEp = epUrl + detectPath

    request = requests.post( urlEp, headers = headers, json = jsonBlock )

    response = request.json()

    jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ' ) )
    detectJsonObj = json.loads( jsonString )

    global detectedLanguage

    detectedLanguage = detectJsonObj[ 0 ][ "language" ]

    # pull list of supported languages to sync up display value

    languageList = getSupportedLanguages( epUrl, langPath )

    displayLanguage = languageList[ detectedLanguage ][ "name" ]

    print( "The language has been detected as ", displayLanguage )

#################################################
# function : translate json block with api call #
#################################################

def translateJsonBlock( jsonBlock, dtcLangCode, trxLangCode, epUrl, translatePath ) :

    endpoint = epUrl + translatePath + "&from=" + dtcLangCode + "&to=" + trxLangCode

    request = requests.post( endpoint, headers = headers, json = jsonBlock )

    response = request.json()

    jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ') )
    translateJsonObj = json.loads( jsonString )

    translatedText = translateJsonObj[ 0 ][ "translations" ][ 0 ][ "text" ]

    print( "Translation : ", translatedText )

#######################
# main body of script #
#######################

toDo = input( "Enter 0 for a document or 1 if typing a phrase : " )

if toDo == "0" :

    # process a document

    DocToProcess = input( "Please enter the location and name of file to be processed : " )

    DocToProcessFmt = magic.from_file( DocToProcess, mime = True )

    workBlock = ConvertDocToJson( DocToProcess, DocToProcessFmt )

elif toDo == "1" :

    # processs a phrase

    PhraseToProcess = input( "Please type the phrase to be processed: " )

    tmpBlock = '[{ "text" : "' + PhraseToProcess + '" }]'

    workBlock = json.loads( tmpBlock )

else :

    print( "Invalid selection." )

    quit()

detectJsonBlock( workBlock, endpoint, detectPath, languagePath )

toTranslate = input( "Would you like to translate the above? Type Yes or No :" )

if toTranslate.upper() == "YES" or ( toTranslate.upper() ).startswith( "Y", 0, 1 ) :

    for key, value in detectedLanguages.items() :

        print( "Supported Language : ", key, " - ", detectedLanguages[ key ][ "name" ] )

    selectTransLang = input( "Please select a language to translate selection into - use provided short code : " )

    if selectTransLang in detectedLanguages :

        translateJsonBlock( workBlock, detectedLanguage, selectTransLang, endpoint, translatePath )

    else :

        print( "Invalid Translation Language Selection." )

        quit()

else :

    print( "Invalid operation selection." )

    quit()

