"""This module is meant to interface with eHost by reading the '.knowtator.xml' files produced by eHost and parsing
them into eHostess.Annotations.Document objects which can be analyzed, possibly using other tools in eHostess."""

from ..Utilities.utilities import cleanDirectoryList
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document, AdjudicationStatus
from ..Utilities.utilities import cleanDirectoryList
from xml.etree import ElementTree
import os
import glob


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


def parseMentionLevelAnnotations(annotationElements, classMentionElements, stringSlotMentionElements):
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

        newAnnotationObj = MentionLevelAnnotation(text, start, end, annotator, annotationId, attributes={}, creationDate=creationDate)
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

def getOriginalFileLength(knowtatorFilePath, searchPaths):
    """This class assumes that fileName is passed as a name without an extension."""
    fileNameWithExt = os.path.split(knowtatorFilePath)[1]
    fileName = fileNameWithExt.split('.')[0]

    # default when no searchPaths are supplied
    if not searchPaths:
        batchDirPath = os.path.split(os.path.split(knowtatorFilePath)[0])[0]
        originalFilePath = os.path.join(batchDirPath, 'corpus', fileName + '.txt')
        with open(originalFilePath, 'r') as infile:
            return len(infile.read())

    filepaths = []
    if not isinstance(searchPaths, list):
        searchPaths = [searchPaths]
    cleanPaths = cleanDirectoryList(searchPaths)
    for path in cleanPaths:
        filepaths.extend(glob.glob(path))

    for filepath in filepaths:
        name = os.path.split(filepath)[1].split('.')[0]
        if name == fileName:
            with open(filepath, 'r') as infile:
                return len(infile.read())

    raise RuntimeError("Could not find %s in the specified paths: %s" % (fileName, searchPaths))

class KnowtatorReader:
    """Because we want to keep track of the total length of a document it is necessary to specify where the original
    document may be found so that its characters may be counted. This class assumes that any file in the search path
    with the same same as the knowtator file is the original document. It will use the first file that it finds. The
    `originalFilesSearchDirs` parameter should be either a path to a single directory, or a list of directory paths. It
    also assumes that the characters in the file are 8-bit characters. By default it assumes that the knowtator files
    are stored in the usual eHost directory structure and that the original files can be found one level up in the
    `corpus` directory. Alternatively a list of search paths can be used to specify the file location. It also assumes
    that the original file has a .txt extension."""
    @classmethod
    def parseMultipleKnowtatorFiles(cls, directoryList, originalFileSearchDirs=None, annotationGroup="MIMC_v2"):
        directoryList = directoryList
        if not isinstance(directoryList, list):
            directoryList = [directoryList]
        if not isinstance(originalFileSearchDirs, list):
            originalFileSearchDirs = [originalFileSearchDirs]
        annotationDocuments = []
        fileNames = []
        cleanDirNames = cleanDirectoryList(directoryList)
        for dirPath in cleanDirNames:
            fileNames.extend(glob.glob(dirPath))

        for filePath in fileNames:
            annotationDocuments.append(cls.parseSingleKnowtatorFile(filePath, originalFileSearchDirs, annotationGroup))
        return annotationDocuments


    @classmethod
    def parseSingleKnowtatorFile(cls, filePath, originalFileSearchDirs=None, annotationGroup="MIMC_v2"):
        """In order to standardize querying and working with notes this  method assigns the document name to be the
        value returned by Document.ParseDocumentNameFromPath()."""
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

        annotations = parseMentionLevelAnnotations(annotationElements, classMentionElements,
                                                   stringSlotMentionElements)
        documentName = Document.ParseDocumentNameFromPath(filePath)
        documentLength = getOriginalFileLength(filePath, originalFileSearchDirs)

        return Document(documentName, annotationGroup, annotations, documentLength, adjudicationStatus=adjudicationStatus)
