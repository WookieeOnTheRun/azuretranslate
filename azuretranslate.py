###################
# import packages #
###################
import requests
import uuid
import json

from requests.api import head
from requests.models import Response # allows reading of MS Word files

from azure.storage.blob import BlobServiceClient
from sqlalchemy import BLANK_SCHEMA

##############################
# create important variables #
##############################
storageEndpoint = ""
storageContainer = "translate-demo"
demoFile = "kafka.txt"
storageSasKey = ""

translateEndpoint = ""
translateKey = ""

serviceRegion = "eastus2" # example region

translatePath = '/translate?api-version=3.0'
detectPath = '/detect?api-version=3.0'
languagePath = '/languages?api-version=3.0&scope=translation'

headers = {
	'Ocp-Apim-Subscription-Key': translateKey,
	'Ocp-apim-subscription-region' : serviceRegion,
	'Content-type': 'application/json',		
	'X-ClientTraceId': str( uuid.uuid4() )
	}

##############################
# create necessary functions #
##############################

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

###############################################################################
# function - convert passed document to json block for use by translation api #
###############################################################################
def ConvertDocToJson( rawText  ) :

    # print( "Initial Raw File : ", rawText )

    charList = [ "\t", "\n", "\r", "\v", "\f" ]

    # print( "Post-Parse Raw File : ", rawFile )

    docText = ""

    docText = rawText # can't remember why docText is being used

    # docText = rawFile.read()

    # docToProcess.close()

    for char in charList :

        docText = docText.replace( char, "" )

    jsonBody = [{ "text" : docText }]
    jsonBlock = jsonBody

    # print( 'Conversion Output : ', jsonBlock )

    # workBlock = json.dump( jsonBlock )

    return jsonBlock;

##############################################
# function : detect json block with api call #
##############################################

def detectJsonBlock( inputBlock, epUrl, detectPath, langPath ) :

    urlEp = epUrl + detectPath

    # let's verify that jsonBlock variable is actually JSON type
    # jsonBlock = json.dumps( inputBlock )
    jsonBlock = inputBlock

    # print( 'Input: ', jsonBlock )

    request = requests.post( urlEp, headers = headers, json = jsonBlock )

    response = request.json()

    print( response )

    jsonString = json.dumps( response, sort_keys = True, ensure_ascii = False, indent = 4, separators = ( ',', ': ' ) )
    detectJsonObj = json.loads( jsonString )

    # print( "Detection Output : ", detectJsonObj )

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

listOfChunks = []

toDo = input( "Enter 0 for a document or 1 if typing a phrase : " )

if toDo == "0" :

    # process a document - script assumes single document for demo

    # DocToProcess = input( "Please enter the location and name of file to be processed : " )
    # DocToProcess = storageEndpoint + storageContainer + "/" + demoFile + storageSasKey

    blobSvcConn = BlobServiceClient( account_url = storageEndpoint, credential = storageSasKey )

    contConn = blobSvcConn.get_container_client( storageContainer )

    blobConn = contConn.get_blob_client( demoFile )

    tmpBlobData = blobConn.download_blob()

    DocToProcess = tmpBlobData.content_as_text()

    # print( "Length: ", len( DocToProcess ) )

    if len( DocToProcess ) > 50000 :

        # break into chunks
        dtpLength = len( DocToProcess )

        # create chunk sizes of 40000, to remain under 50K limit
        dtpChunkSize = 40000

        # determine approx. how many times we'll need to loop through to create chunks
        dtpChunkCount = float( dtpLength / dtpChunkSize )

        # create counter variable to track number of chunks and loops
        counter = 0

        startChunk = 0
        endChunk = dtpChunkSize        

        while ( counter <= dtpChunkCount ) :

            listOfChunks.append( DocToProcess[ startChunk : endChunk ] )

            startChunk += 1
            endChunk = startChunk + 40000

            if ( dtpChunkCount == counter ) :

                # exit if statement
                break

            elif ( float( dtpChunkCount - counter ) < 1 ) :

                counter = dtpChunkCount

            else :

                counter += 1

            print( "Loop Count: ", str( counter ) )

    else :

        listOfChunks.append( DocToProcess )
        # workBlock = ConvertDocToJson( DocToProcess )
        # workBlock = "[{ 'text' : '" + DocToProcess + "' }]"

        # print( type( workBlock ) )
        # print( workBlock )

elif toDo == "1" :

    # processs a phrase

    PhraseToProcess = input( "Please type the phrase to be processed: " )

    workBlock = [{ "text" : PhraseToProcess }]

    listOfChunks.append( workBlock )

else :

    print( "Invalid selection." )

    quit()

# print( 'Pre-Detect : ', workBlock )

for chunkToProcess in listOfChunks :

            workBlock = ConvertDocToJson( str( chunkToProcess ) )

            detectJsonBlock( workBlock, translateEndpoint, detectPath, languagePath )

            toTranslate = input( "Would you like to translate the above? Type Yes or No :" )

            if toTranslate.upper() == "YES" or ( toTranslate.upper() ).startswith( "Y", 0, 1 ) :

                for key, value in detectedLanguages.items() :

                    print( "Supported Language : ", key, " - ", detectedLanguages[ key ][ "name" ] )

                selectTransLang = input( "Please select a language to translate selection into - use provided short code : " )

                if selectTransLang in detectedLanguages :

                    try :

                        translateJsonBlock( workBlock, detectedLanguage, selectTransLang, translateEndpoint, translatePath )

                    except Exception as err :

                        print( "Error with translation :", err )

                else :

                    print( "Invalid Translation Language Selection." )

                    quit()

            else :

                print( "Invalid operation selection." )

                quit()