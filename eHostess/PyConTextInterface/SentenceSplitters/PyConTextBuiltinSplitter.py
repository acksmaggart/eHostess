"""This module contains the logic for splitting sentences and identifying their document span using the built-in PyConText
sentence splitter found in pyConTextNLP.helpers. Due to the whitespace alterations performed by the built-in splitter
it is necessary to use the SentenceReconstructor and SentenceRepeatManager modules to determine the sentence's document
span. You can read more in those two modules about why they are necessary."""

from pyConTextNLP.helpers import sentenceSplitter
from eHostess.PyConTextInterface.SentenceReconstructor import SentenceReconstructor as Reconstructor
from eHostess.PyConTextInterface.SentenceRepeatManager import SentenceRepeatManager as RepeatManger
from PyConTextInput import PyConTextInput
from eHostess.Annotations.Document import Document
import eHostess.Utilities.utilities as utilities
import glob


def _splitSentencesSingleDocInternal(documentPath):
    """Takes a string, returns a list of reconstructed sentences of the form (text, docSpanTuple, docName, docLength, None) to be fed to PyConTextInput."""

    sentenceTuples = []

    with open(documentPath, 'rU') as inFile:
        documentText = inFile.read()

    documentName = Document.ParseDocumentNameFromPath(documentPath)
    docLength = len(documentText)
    sentences = sentenceSplitter().splitSentences(documentText)
    repeatManager = RepeatManger(documentText)
    reconstructor = Reconstructor(documentText)


    for sentence in sentences:
        reconstructedSentence = reconstructor.reconstructSentence(sentence)
        span = repeatManager.determineSpan(reconstructedSentence)

        sentenceTuples.append((reconstructedSentence, span, documentName, docLength, None))
    return sentenceTuples

def splitSentencesSingleDocument(documentPath):
    """
    This function splits the input text into sentences and returns a list of Sentence objects which can be consumed
    by PyConText.
    :param documentText: (string) The path to the note to be split.
    :return: (list) A list of Sentence objects.
    """

    pyConTextInput = PyConTextInput()
    sentenceTuples = _splitSentencesSingleDocInternal(documentPath)

    for sentenceTuple in sentenceTuples:
        pyConTextInput.addSentence(*sentenceTuple)

    return pyConTextInput


def splitSentencesMultipleDocuments(directoryList):
    """This method splits a list of document texts and outputs them in a form that is consumable by
    PyConText.AnnotateMultipleDocuments.

    :param directoryList: (list of strings) A list of directory paths containing notes to split.
    :return: (list of lists) A list of sentence lists, one for each document text.
    """
    if type(directoryList) != list:
        directoryList = [directoryList]

    cleanNames = utilities.cleanDirectoryList(directoryList)
    fileList = [filepath for directory in cleanNames for filepath in glob.glob(directory)]

    sentenceTuples = []
    tupleLists = map(_splitSentencesSingleDocInternal, fileList)
    map(sentenceTuples.extend, tupleLists)

    pyConTextInput = PyConTextInput(numDocs=len(fileList))
    for sentenceTuple in sentenceTuples:
        pyConTextInput.addSentence(*sentenceTuple)

    if not pyConTextInput.containsExpectedNumberOfDocKeys():
        raise RuntimeError("The PyConTextInput object produced by PyConTextBuiltinSplitter does not contain the expected number of documents. Expected: %i, Contains: %i" % (pyConTextInput.numDocs, len(pyConTextInput.keys())))
    return pyConTextInput

