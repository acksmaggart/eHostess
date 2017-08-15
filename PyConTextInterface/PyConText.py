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

def _annotateSentencesInternal(sentenceList, targets, modifiers,
                                    modifierToClassMap, annotationGroup):

    nodeSentenceAnnotationTuples = []

    for sentence in sentenceList:

        markup = pyConText.ConTextMarkup()
        markup.setRawText(sentence.text)
        markup.cleanText()
        markup.markItems(modifiers, mode="modifier")
        markup.markItems(targets, mode="target")
        markup.pruneMarks()
        markup.applyModifiers()
        markup.pruneSelfModifyingRelationships()
        markup.dropInactiveModifiers()

        # Collect all the nodes before making MentionLevelAnnotation objects to check for duplicate nodes. This is
        # necessary in case the TargetSpanSplitter was used.
        for node in markup.nodes():
            if node.getCategory()[0] == 'target':
                # Give annotationId placeholder with specific number to be assigned at the end of the function when we
                # know how many unique annotations we have.
                annotationId = "pyConTextNLP_Instance_"
                attributes = {
                    "certainty": "definite"
                }
                annotationClass = None
                if markup.isModifiedByCategory(node, "NEGATED_EXISTENCE") \
                        and markup.isModifiedByCategory(node, "AFFIRMED_EXISTENCE"):
                    # Currently any node that is marked as both affirmed and negated is considered negated.
                    print("Node is modified by both NEGATED_EXISTENCE and AFFIRMED_EXISTENCE....hmmmm.\n\nNote: %s\nSentence: %s" % (sentence.documentName, sentence.text))
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                elif markup.isModifiedByCategory(node, "NEGATED_EXISTENCE"):
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                # If the node is not modified by NEGATED_EXISTENCE assume it is modified by AFFIRMED_EXISTENCE or it
                # is a target with no modifier and consider it a bleeding_present annotation.
                else:
                    annotationClass = modifierToClassMap["AFFIRMED_EXISTENCE"]
                newAnnotation = MentionLevelAnnotation(sentence.text, sentence.documentSpan[0], sentence.documentSpan[1], "pyConTextNLP",
                                                       annotationId, attributes, annotationClass)
                nodeSentenceAnnotationTuples.append((node, sentence, newAnnotation))


    #Sort the sentences into document groups.
    documentGroups = {}
    for nodeSentenceAnnotationTuple in nodeSentenceAnnotationTuples:
        currentDocumentName = nodeSentenceAnnotationTuple[1].documentName
        if currentDocumentName not in documentGroups:
            documentGroups[currentDocumentName] = []
        documentGroups[currentDocumentName].append(nodeSentenceAnnotationTuple)

    # Ensure that each annotation is unique within its document.
    uniqueDocumentGroups = {}
    for documentGroup in documentGroups.values():
        documentName = documentGroup[0][1].documentName
        uniqueTuples = _removeDuplicateAnnotations(documentGroup)
        uniqueDocumentGroups[documentName] = uniqueTuples

    #Add the appropriate number to the annotation Id's
    for documentGroup in uniqueDocumentGroups.values():
        for index, tuple in enumerate(documentGroup):
            tuple[2].annotationId += str(index)

    #Construct the Document Objects
    documents = []
    for documentGroup in uniqueDocumentGroups.values():
        documentName = documentGroup[0][1].documentName
        documentLength = documentGroup[0][1].documentLength
        annotations = map(list, zip(*documentGroup))[2]
        documents.append(Document(documentName, annotationGroup, annotations, documentLength))

    if len(documents) == 1:
        return documents[0]
    else:
        return documents

def _removeDuplicateAnnotations(nodeSentenceAnnotationTuples):
    """Checks for duplicate nodes by calculating each target's document span and ensuring that they are all unique.
    :return: [list] A list of unique tuples.
    """
    uniqueAnnotations = []
    for tuple in nodeSentenceAnnotationTuples:
        node = tuple[0]
        sentence = tuple[1]

        #Append everything if the targetTerm property is not assigned.
        if sentence.targetRegex == None:
            uniqueAnnotations.append(tuple)
            continue

        if re.match(sentence.targetRegex, node.getPhrase()):
            uniqueAnnotations.append(tuple)

    return uniqueAnnotations

class PyConTextInterface:
    def __init__(self):
        pass


    @classmethod
    def AnnotateSentences(cls, sentences, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on the input Sentence objects and returns a Document object, or a list of Document
        objects if Sentences from multiple notes are passed as input.

        :param sentences: [list] The list of Sentence objects to be annotated, produced using one of the sentence splitters.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: [object | list of objects] A single Document instance if all the sentences share a common documentName or a list of Document
        objects if the input sentences are from multiple notes.
        """

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        return _annotateSentencesInternal(sentences, targets, modifiers,
                                               modifierToClassMap, annotationGroup)

