"""This module is meant to interface with eHost by reading the '.knowtator.xml' files produced by eHost and parsing
them into eHostess.Annotations.Document objects which can be analyzed, possibly using other tools in eHostess."""

import glob
from ..NotePreprocessing.Preprocessor import cleanDirectoryList
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document, AdjudicationStatus
from xml.etree import ElementTree
from xml.etree.cElementTree import Element, SubElement


def evalTrueFalse(string):
    if string.lower() == "false":
        return False
    else:
        return True


def parseAdjudicationStatus(xmlElement):
    options = xmlElement.find("Adjudication_Others")

    overlapping = evalTrueFalse(options.find("CHECK_OVERLAPPED_SPANS").text)
    attributes = evalTrueFalse(options.find("CHECK_ATTRIBUTES").text)
    relationship = evalTrueFalse(options.find("CHECK_RELATIONSHIP").text)
    adjudicationClass = evalTrueFalse(options.find("CHECK_CLASS").text)
    comment = evalTrueFalse(options.find("CHECK_COMMENT").text)

    return AdjudicationStatus(overlapping, attributes, relationship, adjudicationClass, comment)


def parseMentionLevelAnnotations(documentId, annotationElements, classMentionElements, stringSlotMentionElements):
    """This function takes a list of annotation elements, classMention elements, and stringSlotMention elements from
    .knowtator files and combines corresponding elements into MentionLevelAnnotation objects."""
    annotations = {}

    for annotationXml in annotationElements:
        text = annotationXml.find("spannedText").text
        start = annotationXml.find("span").attrib["start"]
        end = annotationXml.find("span").attrib["end"]
        annotator = annotationXml.find("annotator").text
        annotationId = annotationXml.find("mention").attrib["id"]
        creationDate = annotationXml.find("creationDate").text

        newAnnotationObj = MentionLevelAnnotation(documentId, text, start, end, annotator, annotationId, attributes={}, creationDate=creationDate)
        annotations[newAnnotationObj.annotationId] = newAnnotationObj

    for mentionXml in classMentionElements:
        # Get the classMention information.
        mentionId = mentionXml.attrib["id"]
        mentionClass = mentionXml.find("mentionClass").attrib["id"]

        # Get the attributes associated with this classMention.
        stringSlotMentionElementDict = {}
        for stringSlotMentionElement in stringSlotMentionElements:
            id = stringSlotMentionElement.attrib["id"]
            stringSlotMentionElementDict[id] = stringSlotMentionElement

        attributes = {}
        for hasSlotMentionElement in mentionXml.findall("hasSlotMention"):
            stringSlotMentionId = hasSlotMentionElement.attrib["id"]
            stringSlotMentionElement = stringSlotMentionElementDict[stringSlotMentionId]
            key = stringSlotMentionElement.find("mentionSlot").attrib["id"]
            value = stringSlotMentionElement.find("stringSlotMentionValue").attrib["value"]
            attributes[key] = value

        # Update the corresponding annotation object with the classMention information and attributes
        correspondingAnnotation = annotations[mentionId]
        correspondingAnnotation.annotationClass = mentionClass
        correspondingAnnotation.attributes = attributes

    return annotations


class KnowtatorReader:
    @classmethod
    def parseMultipleKnowtatorFiles(cls, directoryList):
        annotationDocuments = []
        fileNames = []
        cleanDirNames = cleanDirectoryList(directoryList)
        for dirPath in cleanDirNames:
            fileNames.extend(glob.glob(dirPath))

        for filePath in fileNames:
            annotationDocuments.append(cls.parseSingleKnowtatorFile(filePath))
        return annotationDocuments


    @classmethod
    def parseSingleKnowtatorFile(cls, filePath):
        fileName = filePath.split('/')[-1]

        tree = ElementTree.parse(filePath)
        root = tree.getroot()
        annotationElements = []
        classMentionElements = []
        stringSlotMentionElements = []
        adjudicationStatus = None
        for child in root:
            if child.tag == "annotation":
                annotationElements.append(child)
            if child.tag == "classMention":
                classMentionElements.append(child)
            if child.tag == "stringSlotMention":
                stringSlotMentionElements.append(child)
            if child.tag == "eHOST_Adjudication_Status":
                adjudicationStatus = parseAdjudicationStatus(child)

        annotations = parseMentionLevelAnnotations(fileName, annotationElements, classMentionElements,
                                                   stringSlotMentionElements)

        return Document(fileName, fileName, annotations, adjudicationStatus=adjudicationStatus)
