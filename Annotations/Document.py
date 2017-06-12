"""This class represents the content and eHost annotation data for a single document. It contains multiple
MentionLevelAnnotation objects, one for each mention level annotation in the document. It may be created by reading an
existing eHost '.knowtator' file, by appending PyConText TagObjects, by appending new MentionLevelAnnotation objects, or
a combination of these options. This class is also capable of serializing its data to produce a '.knowtator' file.
Finally, the class includes the option to check if a set of annotations already exists before appending those
annotations to the document. Each document must have a unique id."""

from xml.etree.cElementTree import Element, SubElement
from xml.etree import ElementTree
from MentionLevelAnnotation import MentionLevelAnnotation

class AdjudicationStatus:
    def __init__(self, overlapping, attributes, relationship, adjudicationClass, comment):
        self.overlapping = overlapping
        self.attributes = attributes
        self.relationship = relationship
        self.adjudicationClass = adjudicationClass
        self.comment = comment

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

def parseMentionLevelAnnotation(annotationHalves, mentionHalves):

    annotations = {}

    for annotationXml in annotationHalves:
        text = annotationXml.find("spannedText").text
        start = annotationXml.find("span").attrib["start"]
        end = annotationXml.find("span").attrib["end"]
        annotator = annotationXml.find("annotator").text
        annotationId = annotationXml.find("mention").attrib["id"]
        annotationId = annotationId.split("_")[-1]
        creationDate = annotationXml.find("creationDate").text

        newAnnotationObj = MentionLevelAnnotation(text, start, end, annotator, annotationId, creationDate=creationDate)
        annotations[newAnnotationObj.annotationId] = newAnnotationObj

    for mentionXml in mentionHalves:
        mentionId = mentionXml.attrib["id"]
        mentionClass = mentionXml.find("mentionClass").attrib["id"]

        parsedId = mentionId.split("_")[-1]
        annotations[parsedId].annotationClass = mentionClass

    return annotations





class Document:
    def __init__(self, documentName, documentId, mentionLevelObjects, adjudicationStatus=None):
        self.documentName = documentName
        # mentionLevelObjects may come in as a list. Internally however, it is stored in a dictionary keyed by
        # annotation id.
        if isinstance(mentionLevelObjects, list):
            annotations = {}
            for annotation in mentionLevelObjects:
                annotations[annotation.annotationId] = annotation
            self.annotations = annotations
        elif isinstance(mentionLevelObjects, dict):
            self.annotations = mentionLevelObjects
        else:
            raise ValueError("The mentionLevelObjects argument must be either a list or a dictionary keyed by" +
                             " annotation ID. Got %s." % type(mentionLevelObjects))
        if not adjudicationStatus:
            self.adjudicationStatus = AdjudicationStatus(False, False, False, False, False)
        else:
            self.adjudicationStatus = adjudicationStatus
	self.documentId = documentId

    @classmethod
    def instantiateFromKnowtator(cls, filePath):
        fileName = filePath.split('/')[-1]

        tree = ElementTree.parse(filePath)
        root = tree.getroot()
        annotationsHalves = []
        mentionClassHalves = []
        adjudicationStatus = None
        for child in root:
            if child.tag == "annotation":
                annotationsHalves.append(child)
            if child.tag == "classMention":
                mentionClassHalves.append(child)
            if child.tag == "eHOST_Adjudication_Status":
                adjudicationStatus = parseAdjudicationStatus(child)

        annotations = parseMentionLevelAnnotation(annotationsHalves, mentionClassHalves)

        return cls(fileName, annotations, adjudicationStatus=adjudicationStatus)


    def getNextAnnotationId(self):
        """Sorts annotation objects by id and returns the highest + 1."""
        ids = list(self.annotations).sort()
        highest = ids[-1]
        return int(highest) + 1


    def serializeToKnowtatorXML(self, outDir, fileName):
        """Annotation IDs are stored internally as integers. They should be converted to 'EHOST_Instance_%d' % id to
         be consistent with eHosts xml format. Information about the origin of the annotation should be contained in
         the mention class."""

    @classmethod
    def discrepancies(cls, firstDocument, secondDocument):
        """Returns two new documents containing the symmetric differences of the annotation sets represented by the
         input documents. Specifically, the first output document will contain all the annotations that were in
         firstDocument but not in secondDocument and the second output document will contain all the annotations that
         were in secondDocument but not in firstDocument. One limitation with this method is that if multiple annotations
         from one document overlap with a single annotation from the other document this algorithm will not detect the
         discrepancy. This is not a problem if the annotators only highlight the term and not the context of the term."""

        firstOutputAnnotations = []
        secondOutputAnnotations = []

        # first run comparison with firstDocument as outer.
        for outerKey in firstDocument.annotations:
            outerAnnotation = firstDocument.annotations[outerKey]
            for innerKey in secondDocument.annotations:
                innerAnnotation = secondDocument.annotations[innerKey]
                # If the outer annotation overlaps the inner annotation go on to the next outer annotation.
                if MentionLevelAnnotation.overlap(outerAnnotation, innerAnnotation):
                    break
            # if the outer annotation does not find an overlapping inner annotation add it to the list of discrepancies.
            firstOutputAnnotations.append(outerAnnotation)

        # next run comparison with secondDoc as outer.
        for outerKey in secondDocument.annotations:
            outerAnnotation = secondDocument.annotations[outerKey]
            for innerKey in firstDocument.annotations:
                innerAnnotation = firstDocument.annotations[innerKey]
                if MentionLevelAnnotation.overlap(outerAnnotation, innerAnnotation):
                    break
            secondOutputAnnotations.append(outerAnnotation)

        outputDoc1 = Document("DiscrepancyOutput1", firstOutputAnnotations)
        outputDoc2 = Document("DiscrepancyOutput2", secondOutputAnnotations)

        return outputDoc1, outputDoc2


    @classmethod
    def mergeDocuments(cls, firstDocument, secondDocument):
        """Creates a new document that combines the two input documents. This method does not check for duplicates after
        combining the documents. If the user wishes to produce the union of two documents they must first use
        Document.discrepancies()."""


