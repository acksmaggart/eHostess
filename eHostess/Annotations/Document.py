
from xml.etree.cElementTree import Element, SubElement
from xml.etree import ElementTree
from .MentionLevelAnnotation import MentionLevelAnnotation


class AdjudicationStatus:
    """
    This class is effectively a struct that contains the eHost adjudication status information found in eHost '.knowtator.xml' files. Each Document instance contains an instance of AdjudiationStatus so that it may be serialized into a '.knowtator.xml' file using eHostInteface.KnowtatorWriter. This information is only useful if the user plans to perform adjudication using eHost. All values default to False.

    :param overlapping: [bool] True if the user wishes to check for overlapping spans or False if the user only wants to count identical spans as a match.
    :param attributes:  [bool] True if the user wants to include annotation attributes in a match determination.
    :param relationship: [bool] True if the user wants to include relationship information in a match determination.
    :param adjudicationClass: [bool] True if the user wants to include annotation class in a match determination.
    :param comment: [bool] True if the user wants to include the annotation comments in a match determination.
    """

    def __init__(self, overlapping=False, attributes=False, relationship=False, adjudicationClass=False,
                 comment=False):
        self.overlapping = overlapping
        self.attributes = attributes
        self.relationship = relationship
        self.adjudicationClass = adjudicationClass
        self.comment = comment


class Document:
    """
    This class represents the annotation data for a single document. It contains multiple MentionLevelAnnotation objects, one for each mention level annotation in the document. While instances of this class may be created by calling the constructor directly it is designed to be used with factory classes such as :class:`KowtatorReader <eHostess.eHostInterface.KnowtatorReader.KnowtatorReader>` which parses .knowtator files and returns an array of Document objects.

    :param documentName: [string] The name you want the document to have.
    :param annotationGroup: [string] The annotation group that the document will belong to.
    :param mentionLevelObjects: [list] A list of MentionLevelAnnotation objects. These will be the document's annotations.
    :param numberOfCharacters: [int] The number of characters in the document.
    :param adjudicationStatus: [object] An instance of :class:`AdjudicationStatus <eHostess.Annotations.Document.AdjudicationStatus>`. Useful only if you plan to perform adjudication using eHost. Defaults all adjudication values to False.
    """

    def __init__(self, documentName, annotationGroup, mentionLevelObjects, numberOfCharacters, adjudicationStatus=None):
        self.documentName = documentName

        if not isinstance(mentionLevelObjects, list):
            raise ValueError("The mentionLevelObjects argument must be list. Got %s." % type(mentionLevelObjects))
        self.annotations = mentionLevelObjects
        if not adjudicationStatus:
            self.adjudicationStatus = AdjudicationStatus()
        else:
            self.adjudicationStatus = adjudicationStatus
        self.annotationGroup = annotationGroup
        self.numberOfCharacters = numberOfCharacters

    @classmethod
    def discrepancies(cls, firstDocument, secondDocument):
        """
        Returns two new documents containing the symmetric differences of the annotation sets represented by the input documents. Specifically, the first output document will contain all the annotations that were in firstDocument but not in secondDocument and the second output document will contain all the annotations that were in secondDocument but not in firstDocument. One limitation with this method is that if multiple annotations from one document overlap with a single annotation from the other document this algorithm will not detect the discrepancy. This is not a problem if the annotators only highlight the term and not the context of the term.

        :param firstDocument: [object] An instance of Document.
        :param secondDocument: [object] A second instance of Document.
        :return: [tuple] A 2-tuple of new documents with the annotations that were unique to each input document. The order of documents is preserved, i.e. the first output document corresponds to the first input document and the second output document corresponds to the second input document.
        """

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

        outputDoc1 = cls("DiscrepancyOutput1", firstOutputAnnotations)
        outputDoc2 = cls("DiscrepancyOutput2", secondOutputAnnotations)

        return outputDoc1, outputDoc2

    @classmethod
    def mergeDocuments(cls, firstDocument, secondDocument):
        """Creates a new document that combines the two input documents. This method does not check for duplicates after
        combining the documents. If the user wishes to produce the union of two documents they must first use
        Document.discrepancies()."""
        raise NotImplementedError("Document.mergeDocuments is not implemented.")

    @classmethod
    def ParseDocumentNameFromPath(cls, filePath):
        """This method is used to create document names. Rather than implementing several, possibly conflicting, document
        naming policies throughout the code it is centralized here. Anytime a class needs to produce a Document name it
        should use this classmethod.
        The current implementation returns the name of the file without the extension(s). For example::

            >>> Document.ParseDocumentNameFromPath('/Path/To/The/Annotations/Named/149875.xml.knowtator')
            '149875'

        :param filePath: [string] A document path to clean.
        :return: [string] A clean document name.
        """
        return filePath.split('/')[-1].split('.')[0]

class ClassifiedDocument(Document):
    def __init__(self, documentName, annotationGroup, mentionLevelObjects, numberOfCharacters, documentClass, adjudicationStatus=None):
        """
        This class represents a document which has been classified, presumably in preparation for performing some kind of supervised learning or other analysis that requires data to be accompanied by class labels. Given the variety of classification methods and the likelihood that the details of each use case may vary widely it is intended that eHostess users will write custom logic to convert their Document objects to ClassifiedDocument objects. Once the user is in possession of ClassifiedDocument objects they may avail themselves of the more generalized analysis functions available in eHostess.Analysis (which consume these objects) or of course create their own analysis scripts.

    :param documentName: [string] The name you want the document to have.
    :param annotationGroup: [string] The annotation group that the document will belong to.
    :param mentionLevelObjects: [list] A list of MentionLevelAnnotation objects. These will be the document's annotations.
    :param numberOfCharacters: [int] The number of characters in the document.
    :param documentClass: [string] The class with which this document has been labeled, e.g. "positive", "negative", "group_1", etc. The inclusion of this attribute facilitates many types of document analyses.
    :param adjudicationStatus: [object] An instance of :class:`AdjudicationStatus <eHostess.Annotations.Document.AdjudicationStatus>`. Useful only if you plan to perform adjudication using eHost. Defaults all adjudication values to False.
        """
        Document.__init__(self, documentName, annotationGroup, mentionLevelObjects, numberOfCharacters)
        self.documentClass = documentClass

    @classmethod
    def CreateFromDocument(cls, document, documentClass):
        """
        This his a convenience method for creating a ClassifiedDocument from a regular Document. This is useful in cases where the process of document classification does not involve altering the list of MentionLevelAnnotations. This method simply calls the ClassifiedDocument constructor passing the input 'document's attributes as arguments along with the supplied 'documentClass'.
        :param document: [object] An instance of Document.
        :param documentClass: [string] The class with which this document has been labeled.
        :return: [object] An instance of ClassifiedDocument.
        """

        return cls(document.documentName, document.annotationGroup, document.annotations, document.numberOfCharacters, documentClass, document.adjudicationStatus)

