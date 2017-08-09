"""
This module serves as the interface to pyConText. It executes the pyConTextNLP package on the contents of text documents using the supplied modifiers and targets found either at the specified paths or at the default location in the TargetsAndModifiers directory which should be in the same directory as this module.

It uses the "defaultModifierToAnnotationClassMap" to convert pyConText target and modifier types to eHost annotation classes. For example, annotations marked as "NEGATED_EXISTENCE" by pyConText would be instantiated as"MentionLevelAnnotation"s with the class "bleeding_absent", if "bleeding_absent" were your eHost annotation class.

Currently this module assigns attributes of ::

    { "certainty" : "definite" }

to all the annotations it creates.

"""

from pyConTextNLP import pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
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

def _annotateSingleDocumentInternal(sentenceList, targets, modifiers,
                                    modifierToClassMap, annotationGroup):

    mentionLevelAnnotations = []

    for sentence in sentenceList:
        escapedSentence = re.escape(sentence.text)

        markup = pyConText.ConTextMarkup()
        markup.setRawText(sentence)
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
                sentenceStart = sentence.span[0]
                documentSpan = (annotationSpan[0] + sentenceStart, annotationSpan[1] + sentenceStart)
                text = sentence
                annotationId = "pyConTextNLP_Instance_" + str(len(mentionLevelAnnotations) + 1)
                attributes = {
                    "certainty": "definite"
                }
                annotationClass = None
                if markup.isModifiedByCategory(node, "NEGATED_EXISTENCE") \
                        and markup.isModifiedByCategory(node, "AFFIRMED_EXISTENCE"):

                    print("Node is modified by both NEGATED_EXISTENCE and AFFIRMED_EXISTENCE....hmmmm.\n\nNote: %s\nSentence: %s" % (sentence.documentName, sentence.text))
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                elif markup.isModifiedByCategory(node, "NEGATED_EXISTENCE"):
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                # If the node is not modified by NEGATED_EXISTENCE assume it is modified by AFFIRMED_EXISTENCE or it
                # is a target with no modifier and consider it a bleeding_present annotation.
                else:
                    annotationClass = modifierToClassMap["AFFIRMED_EXISTENCE"]
                newAnnotation = MentionLevelAnnotation(text, documentSpan[0], documentSpan[1], "pyConTextNLP",
                                                       annotationId, attributes, annotationClass)
                mentionLevelAnnotations.append(newAnnotation)

    newDocument = Document(sentenceList[0].documentName, annotationGroup, mentionLevelAnnotations, sentenceList[0].documentLength)
    # Delete duplicates in case the document was annotated using output from the span-based splitter.
    newDocument.removeDuplicates()
    return newDocument


class PyConTextInterface:
    def __init__(self):
        pass


    @classmethod
    def AnnotateSingleDocument(cls, sentences, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on the input sentence objects and returns a Document object.

        :param sentences: [list] The list of Sentence objects to be annotated, produced using one of the sentence splitters.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: A single Document instance.
        """

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        return _annotateSingleDocumentInternal(sentences, targets, modifiers,
                                               modifierToClassMap, annotationGroup)


    @classmethod
    def AnnotateMultipleDocuments(cls, sentenceLists, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on multiple notes and returns a list of Documents.

        :param sentenceLists: [list of strings] A list of lists of sentence objects, e.g. as produced by
        PyConTextBuiltinSplitter.SplitSentencesMultipleDocuments.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: A single Document instance.
        """

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        annotationDocuments = []

        for sentenceList in sentenceLists:
            annotationDocuments.append(_annotateSingleDocumentInternal(sentenceList, targets, modifiers,
                                                                       modifierToClassMap, annotationGroup))

        return annotationDocuments