"""This module contains the logic for splitting sentences and identifying their document span using the built-in PyConText
sentence splitter found in pyConTextNLP.helpers. Due to the whitespace alterations performed by the built-in splitter
it is necessary to use the SentenceReconstructor and SentenceRepeatManager modules to determine the sentence's document
span. You can read more in those two modules about why they are necessary."""

from pyConTextNLP.helpers import sentenceSplitter
from eHostess.PyConTextInterface.SentenceReconstructor import SentenceReconstructor as Reconstructor
from eHostess.PyConTextInterface.SentenceRepeatManager import SentenceRepeatManager as RepeatManger
from Sentence import Sentence


def splitSentencesSingleDocument(documentText, documentName):
    """
    This function splits the input text into sentences and returns a list of Sentence objects which can be consumed
    by PyConText.
    :param documentText: (string) The raw note body to split.
    :return: (list) A list of Sentence objects.
    """

    sentences = sentenceSplitter().splitSentences(documentText)
    repeatManager = RepeatManger(documentText)
    reconstructor = Reconstructor(documentText)

    sentenceObjects = []
    for sentence in sentences:
        reconstructedSentence = reconstructor.reconstructSentence(sentence)
        span = repeatManager.determineSpan(reconstructedSentence)

        sentenceObjects.append(Sentence(reconstructedSentence, span, documentName, len(documentText)))

    return sentenceObjects


def splitSentencesMultipleDocuments(textList):
    """This method splits a list of document texts and outputs them in a form that is consumable by
    PyConText.AnnotateMultipleDocuments.

    :param textList: (list of strings) A list of document texts.
    :return: (list of lists) A list of sentence lists, one for each document text.
    """
    return [splitSentencesSingleDocument(text) for text in textList]

