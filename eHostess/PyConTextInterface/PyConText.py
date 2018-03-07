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
from .SentenceSplitters.PyConTextInput import DocumentPlaceholder
import re
import os
from collections import namedtuple


defaultModifierToAnnotationClassMap = {
    "NEGATED_EXISTENCE" : "bleeding_absent",
    "AFFIRMED_EXISTENCE" : "bleeding_present"
}

defaultTargetFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/targets.tsv'
defaultModifiersFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/modifiers.tsv'

AnnotationTrio = namedtuple('AnnotationTrio', ['node', 'sentence', 'annotation'])

def _annotateSentences(sentenceList, targets, modifiers, modifierToClassMap, annotationGroup):
    """Takes a list of sentence objects that all belong to the same document and returns a list of tuples, all of the form (<PyConText Node>, <Sentence Object>, <MentionLevelAnnotation>). If isinstance(sentenceList, DocumentPlaceholder) this function returns an empty list. Similarly, if no annotations are produced by processing the sentences, this function returns an empty list."""
    annotationTrioTuples = []

    if isinstance(sentenceList, DocumentPlaceholder):
        return annotationTrioTuples

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
                if markup.isModifiedByCategory(node, "NEGATED_EXISTENCE") and markup.isModifiedByCategory(node, "AFFIRMED_EXISTENCE"):
                    # Currently any node that is marked as both affirmed and negated is considered negated.
                    print(
                    "Node is modified by both NEGATED_EXISTENCE and AFFIRMED_EXISTENCE....hmmmm.\n\nNote: %s\nSentence: %s" % (
                    sentence.documentName, sentence.text))
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                elif markup.isModifiedByCategory(node, "NEGATED_EXISTENCE"):
                    annotationClass = modifierToClassMap["NEGATED_EXISTENCE"]
                # If the node is not modified by NEGATED_EXISTENCE assume it is modified by AFFIRMED_EXISTENCE or it
                # is a target with no modifier and consider it a bleeding_present annotation.
                else:
                    annotationClass = modifierToClassMap["AFFIRMED_EXISTENCE"]
                predecessorList = markup.predecessors(node)
                predecessorPhrases = []
                for predecessor in predecessorList:
                    predecessorPhrases.append(predecessor.getPhrase())
                targetDict = {"modifiers": predecessorPhrases, "target": node.getPhrase()}
                newAnnotation = MentionLevelAnnotation(sentence.text, sentence.documentSpan[0],
                                                       sentence.documentSpan[1], "pyConTextNLP",
                                                       annotationId, attributes, annotationClass, dynamicProperties=targetDict)
                annotationTrioTuples.append(AnnotationTrio(node, sentence, newAnnotation))

    return annotationTrioTuples


def _performAnnotationInternal(inputObject, targets, modifiers, modifierToClassMap, annotationGroup):

    # Convert each list of sentences into AnnotationTrio tuples and hash them by document name.
    tuplesGroupedByDoc = {}
    for key in inputObject.keys():
        docName = key
        annotationTrioTuples = _annotateSentences(inputObject[key], targets, modifiers, modifierToClassMap, annotationGroup)

        tuplesGroupedByDoc[docName] = annotationTrioTuples


    # Ensure that each annotation is unique within its document.
    uniqueDocumentGroups = {}
    for documentName in tuplesGroupedByDoc:
        uniqueTuples = _removeDuplicateAnnotations(tuplesGroupedByDoc[documentName])
        uniqueDocumentGroups[documentName] = uniqueTuples

    #Add the appropriate number to the annotation Id's
    for documentName in uniqueDocumentGroups:
        for index, annotationTrio in enumerate(uniqueDocumentGroups[documentName]):
            annotationTrio.annotation.annotationId += str(index)

    #Construct the Document Objects
    documents = []
    for documentName in uniqueDocumentGroups:
        newDocument = None
        # The document did not produce any sentences or did not produce any annotations.
        if len(uniqueDocumentGroups[documentName]) == 0:
            newDocument = Document(documentName, annotationGroup, [], 0)
        else:
            firstTrio = uniqueDocumentGroups[documentName][0]
            documentLength = firstTrio.sentence.documentLength
            annotations = map(list, zip(*uniqueDocumentGroups[documentName]))[2]
            newDocument = Document(documentName, annotationGroup, annotations, documentLength)
        documents.append(newDocument)

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

        if re.match(sentence.targetRegex, node.getPhrase(), re.IGNORECASE):
            uniqueAnnotations.append(tuple)

    return uniqueAnnotations

class PyConTextInterface:
    def __init__(self):
        pass


    @classmethod
    def PerformAnnotation(cls, pyConTextInputObject, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath,
                               modifierToClassMap=defaultModifierToAnnotationClassMap, annotationGroup="MIMC_v2"):
        """
        This method runs PyConText on the input Sentence objects and returns a Document object, or a list of Document
        objects if Sentences from multiple notes are passed as input.

        :param pyConTextInputObject: [object] An instance of PyConTextInput produced by one of the sentence splitters containing sentences to be split.
        :param targetFilePath: [string] The path to the tsv file containing the PyConText target terms.
        :param modifiersFilePath: [string] The path to the tsv file containing the PyConText modifier terms.
        :param modifierToClassMap: [dict] A dictionary used to map eHost classes to pyConText modifier types.
        :param annotationGroup: [string] The current annotation round.
        :return: [object | list of objects] A single Document instance if all the sentences share a common documentName or a list of Document
        objects if the input sentences are from multiple notes.
        """

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        return _performAnnotationInternal(pyConTextInputObject, targets, modifiers,
                                               modifierToClassMap, annotationGroup)

