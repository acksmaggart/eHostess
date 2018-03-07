

from .PyConTextInput import PyConTextInput
from eHostess.Annotations.Document import Document
import spacy
import en_core_web_sm
import os
import sys
import re

nlp = en_core_web_sm.load()

def _splitSentencesInternal(documentPath):
    """Splits a single document."""
    if not os.path.isfile(documentPath):
        raise RuntimeError("File not found: %s" % documentPath)
    with open(documentPath, "rU") as f:
        body = f.read()
    docLength = len(body)
    docName = Document.ParseDocumentNameFromPath(documentPath)
    doc = nlp(unicode(body)) # Necessary in Python2.7
    #doc = nlp(body) # Necessary in python3.6
    sentences = []
    for sent in doc.sents:
        text = sent.text
        span = (sent.start_char, sent.end_char)
        sentences.append((text, span, docName, docLength))
    return sentences

def _splitSentencesInternalRawString(body, name):
    """Splits a raw string."""
    docLength = len(body)
    docName = name
    doc = nlp(unicode(body)) # Necessary in Python2.7
    #doc = nlp(body) # Necessary in python3.6
    sentences = []
    for sent in doc.sents:
        text = sent.text
        span = (sent.start_char, sent.end_char)
        sentences.append((text, span, docName, docLength))
    return sentences

def splitSentencesSingleDocument(documentPath):
    inputObj = PyConTextInput()
    inputObj.addSentence(*_splitSentencesInternal(documentPath)[0])
    return inputObj

def splitSentencesMultipleDocuments(documentPaths):
    inputObj = PyConTextInput()

    numDocs = len(documentPaths)
    for index, docPath in enumerate(documentPaths):
        sys.stdout.write("\rSplitting document %i of %i. (%.3f%%)" % (index + 1, numDocs, float(index + 1) * 100. / float(numDocs)))
        for sentenceInfo in _splitSentencesInternal(docPath):
            inputObj.addSentence(*sentenceInfo)

    return inputObj

def splitSentencesRawString(string, documentName):
    inputObj = PyConTextInput()
    for sentenceInfo in _splitSentencesInternalRawString(string, documentName):
        inputObj.addSentence(*sentenceInfo)
    return inputObj

