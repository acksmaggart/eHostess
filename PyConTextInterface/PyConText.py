"""
This module serves as the interface to pyConText. It executes the pyConTextNLP package on the contents of text documents using the supplied modifiers and targets found either at the specified paths or at the default location in the TargetsAndModifiers directory which should be in the same directory as this module.

It uses the "defaultModifierToAnnotationClassMap" to convert pyConText target and modifier types to eHost annotation classes. For example, annotations marked as "NEGATED_EXISTENCE" by pyConText would be instantiated as"MentionLevelAnnotation"s with the class "bleeding_absent", if "bleeding_absent" were your eHost annotation class.

Currently this module assigns attributes of ::

    { "certainty" : "definite" }

to all the annotations it creates.

"""

from pyConTextNLP import pyConTextGraph as pyConText
from pyConTextNLP.helpers import sentenceSplitter
import pyConTextNLP.itemData as itemData
from SentenceRepeatManager import SentenceRepeatManager
from SentenceReconstructor import SentenceReconstructor
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document
from ..Utilities.utilities import cleanDirectoryList
import glob
import re
import os


defaultModifierToAnnotationClassMap = {
    "NEGATED_EXISTENCE" : "bleeding_absent",
    "AFFIRMED_EXISTENCE" : "bleeding_present"
}

defaultTargetFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/targets.tsv'
defaultModifiersFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/modifiers.tsv'

def _annotateSingleDocumentInternal(documentFilePath, targets, modifiers, sentenceSplitter,
                                    modifierToClassMap, annotationGroup):
    """Here is  another method."""
    inFileHandle = open(documentFilePath, mode='rU')
    noteBody = inFileHandle.read()
    numChars = len(noteBody)
    inFileHandle.close()

    repeatManager = SentenceRepeatManager()
    sentenceReconstructor = SentenceReconstructor(noteBody)
    sentences = sentenceSplitter().splitSentences(noteBody)
    mentionLevelAnnotations = {}

    for sentence in sentences:
        reconstructedSentence = sentenceReconstructor.reconstructSentence(sentence)
        escapedSentence = re.escape(reconstructedSentence)
        matches = re.findall(escapedSentence, noteBody)
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
                text = sentence
                annotationId = "pyConTextNLP_Instance_" + str(len(mentionLevelAnnotations) + 1)
                attributes = {
                    "certainty": "definite"
                }
                annotationClass = None
                if markup.isModifiedByCategory(node, "NEGATED_EXISTENCE") \
                        and markup.isModifiedByCategory(node, "AFFIRMED_EXISTENCE"):

                    print("Node is modified by both NEGATED_EXISTENCE and AFFIRMED_EXISTENCE....hmmmm.\n\nNote: %s\nSentence: %s" % (documentFilePath, reconstructedSentence))
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                elif markup.isModifiedByCategory(node, "NEGATED_EXISTENCE"):
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                # If the node is not modified by NEGATED_EXISTENCE assume it is modified by AFFIRMED_EXISTENCE or it
                # is a target with no modifier and consider it a bleeding_present annotation.
                else:
                    annotationClass = modifierToClassMap["AFFIRMED_EXISTENCE"]
                newAnnotation = MentionLevelAnnotation(text, documentSpan[0], documentSpan[1], "pyConTextNLP",
                                                       annotationId, attributes, annotationClass)
                mentionLevelAnnotations[annotationId] = newAnnotation

    documentName = Document.ParseDocumentNameFromPath(documentFilePath)
    return Document(documentName, annotationGroup, mentionLevelAnnotations, numChars)

class PyConTextInterface:
    def __init__(self):
        pass


    @classmethod
    def AnnotateSingleDocument(cls, documentFilePath, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath, sentenceSplitter=sentenceSplitter,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on the specified note and returns a Document object.

        :param documentFilePath: [string] The relative or absolute path to the note.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param sentenceSplitter: [Class] The class possessing a class method called "splitSentences()", used to split the sentences of the target note.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: A single Document instance.
        """

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        return _annotateSingleDocumentInternal(documentFilePath, targets, modifiers, sentenceSplitter,
                                               modifierToClassMap, annotationGroup)


    @classmethod
    def AnnotateMultipleDocuments(cls, directoryPaths, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath, sentenceSplitter=sentenceSplitter,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on multiple notes and returns a list of Documents.

        :param directoryPaths: [string | list of strings] A list of directories containing notes to be annotated.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param sentenceSplitter: [Class] The class possessing a class method called "splitSentence()", used to split the sentences of the target note.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: A single Document instance.
        """

        if not isinstance(directoryPaths, list):
            directoryPaths = [directoryPaths]

        cleanPaths = cleanDirectoryList(directoryPaths)
        filePathList = []

        for dirpath in cleanPaths:
            filePathList.extend(glob.glob(dirpath))

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        annotationDocuments = []

        for filepath in filePathList:
            annotationDocuments.append(_annotateSingleDocumentInternal(filepath, targets, modifiers, sentenceSplitter,
                                                                       modifierToClassMap, annotationGroup))

        return annotationDocuments