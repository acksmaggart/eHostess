"""
This module serves as the interface to pyConText. It executes the pyConTextNLP package on the contents of text documents
using the supplied modifiers and targets found either at the specified paths or at the default location in the
TargetsAndModifiers directory which should be in the same directory as this module.

It uses the `defaultModifierToAnnotationClassMap` to convert pyConText target and modifier types to eHost annotation
classses. For example, annotations marked as "NEGATED_EXISTENCE" by pyConText would be instantiated as
`MentionLevelAnnotation`s with the class "bleeding_absent", if "bleeding_absent" were your eHost annotation class.

Currently this module assigns attributes of
                            "certainty" : "definite",
                            "manual_v_auto" : "manual"
to all the annotations it creates.
"""

from pyConTextNLP import pyConTextGraph as pyConText
from pyConTextNLP.helpers import sentenceSplitter
import pyConTextNLP.itemData as itemData
from SentenceRepeatManager import SentenceRepeatManager
from SentenceReconstructor import SentenceReconstuctor
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document
import re
import os


defaultModifierToAnnotationClassMap = {
    "NEGATED_EXISTENCE" : "bleeding_absent",
    "AFFIRMED_EXISTENCE" : "bleeding_present"
}

defaultTargetFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/targets.tsv'
defaultModifiersFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/modifiers.tsv'

class PyConTextInferface:
    def __init__(self):
        self.stuff = "stuff"


    @classmethod
    def AnnotateSingleDocument(cls, documentFilePath, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath, sentenceSplitter=sentenceSplitter,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        inFileHandle = open(documentFilePath, 'r')
        noteBody = inFileHandle.read()
        inFileHandle.close()

        repeatManager = SentenceRepeatManager()
        sentenceReconstructor = SentenceReconstuctor(noteBody)
        sentences = sentenceSplitter().splitSentences(noteBody)
        mentionLevelAnnotations = {}


        for sentence in sentences:
            reconstructedSentence = sentenceReconstructor.reconstructSentence(sentence)
            matches = re.findall(re.escape(reconstructedSentence), noteBody)
            sentenceSpan = None
            if not matches:
                print("eHostess/PyConTextInterface/PyConText: Did not find sentence in text, something is wrong.")
                print("Note: %s" % documentFilePath)
                print("Sentence:")
                print(sentence + '\n')
                exit(1)

            # if the sentence appears multiple times in the note we need to make sure we grab them all instead of grabbing
            # the first one multiple times.
            if len(matches) > 1:
                sentenceSpan = repeatManager.processSentence(reconstructedSentence, noteBody)

            else:
                # if there is only once instance of the sentence, proceed as normal. It is necessary to re-perform the
                # search using re.search() instead of re.findall() in order to get the span.
                match = re.search(re.escape(reconstructedSentence), noteBody)
                start = match.start()
                end = match.end()
                sentenceSpan = (start, end)

            markup = pyConText.ConTextMarkup()
            markup.setRawText(reconstructedSentence)
            markup.cleanText()
            markup.markItems(modifiers, mode="modifier")
            markup.markItems(targets, mode="target")
            markup.pruneMarks()
            markup.applyModifiers()
            markup.pruneSelfModifyingRelationships()
            markup.dropInactiveModifiers()

            for node in markup.nodes():
                if node.getCategory()[0] == 'target':

                    annotationSpan = node.getSpan()
                    sentenceStart = sentenceSpan[0]
                    documentSpan = (annotationSpan[0] + sentenceStart, annotationSpan[1] + sentenceStart)
                    text = node.getPhrase()
                    annotationId = "pyConTextNLP_Instance_" + str(len(mentionLevelAnnotations) + 1)
                    attributes = {
                        "certainty": "definite",
                        "manual_v_auto": "manual"
                    }
                    annotationClass = None
                    if markup.isModifiedByCategory(node, "NEGATED_EXISTENCE") and markup.isModifiedByCategory(node, "AFFIRMED_EXISTENCE"):
                        raise RuntimeError("Node is modified by both NEGATED_EXISTENCE and AFFIRMED_EXISTENCE....hmmmm. Sentence: %s"
                                           % reconstructedSentence)
                    elif markup.isModifiedByCategory(node, "NEGATED_EXISTENCE"):
                        annotationClass = defaultModifierToAnnotationClassMap["NEGATED_EXISTENCE"]
                    # If the node is not modified by NEGATED_EXISTENCE assume it is modified by AFFIRMED_EXISTENCE or it
                    # is a target with no modifier and consider it a bleeding_present annotation.
                    else:
                        annotationClass = defaultModifierToAnnotationClassMap["AFFIRMED_EXISTENCE"]
                    newAnnotation = MentionLevelAnnotation(text, documentSpan[0], documentSpan[1], "pyConTextNLP",
                                                           annotationId, attributes, annotationClass)
                    mentionLevelAnnotations[annotationId] = newAnnotation


        documentName = Document.ParseDocumentNameFromPath(documentFilePath)
        return Document(documentName, annotationGroup, mentionLevelAnnotations)

    @classmethod
    def AnnotateMultipleDocuments(cls, directoryPaths):
        if not isinstance(directoryPaths, list):
            directoryPaths = [directoryPaths]
        