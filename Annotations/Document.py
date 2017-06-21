"""This class represents the annotation data for a single document. It contains multiple
MentionLevelAnnotation objects, one for each mention level annotation in the document. While instances of this class may
 be created by calling the constructor directly it is designed to be used with factory classes such as
 eHostess.eHostInterface.KnowtatorReader which parses .knowtator files and returns an array of Document objects."""

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


class Document:
    def __init__(self, documentName, annotationGroup, mentionLevelObjects, adjudicationStatus=None):
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
        self.annotationGroup = annotationGroup

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

    @classmethod
    def ParseDocumentNameFromPath(cls, filePath):
        """This method is used to create document names. Rather than implementing several, possibly conflicting, document
        naming policies throughout the code it is centralized here. Anytime a class needs to produce a Document name it
        should use this classmethod.
        The current implementation returns the name of the file without the extension(s)."""
        return filePath.split('/')[-1].split('.')[0]
