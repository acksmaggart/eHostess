"""
This module is designed to compare two documents, or two sets of documents, and to report the annotations that do or do not match between corresponding documents.
"""

from ..Annotations.Document import Document
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
import numpy as np


def allAttributesMatch(annotation1, annotation2):
    if len(annotation1.attributes) != len(annotation2.attributes):
        return False

    for attribKey1 in annotation1.attributes:
        if attribKey1 not in annotation2.attributes:
            return False
        if annotation1.attributes[attribKey1] != annotation2.attributes[attribKey1]:
            return False

    return True

ComparisonResults ={
    "1" : "No Overlap",
    "2" : "Class Mismatch",
    "3" : "Attribute Mismatch",
    "4" : "Class and Attribute Mismatch",
    "5" : "Match"
    }

class Comparison:
    """
    This class is meant to compare two :class:`Document <eHostess.Annotations.Document.Document>` objects and to report their discrepancies. A discrepancy is defined as either of the following cases:
    1. An annotation in one document does not overlap with any annotations in the other document.
    2. An annotation in one document has class or attribute mismatches with all overalapping annotations in the other document.

    Implicitly then, a match is defined as a pair of annotations whose spans overlap and whose classes and attributes all match. The algorithm implemented in this module assumes that if two annotations overlap and share their classes and all attributes in common they are matches, even if there may be multiple overlapping annotations. This could also be a problem if two annotators highlighted the same span which contained two different terms, and their intended term was different from the other annotator's intended term. This would produce a situation in which there were really two mismatches but it got recorded as a single match. This flaw was judged to be acceptable since the odds of its occurrence are low and the document-level classification is more important and immune to this possibility anyway. The second case that will produce an error is if there are multiple terms in quick succession and one annotator highlights them all as a single annotation while the other annotates each one individually. The first annotation created by the second annotator will match the first annotator's long annotation and the rest of the smaller annotations will show up as mismatches. This is of course not desireable, however, it has yet to be determined if it constitutes a problem worth fixing.

    :param documentName: [string] Typically a user wishes to compare two sets of annotations produced from the same note. This parameter is the name of that note.
    :param comparisonResult: [string] One of the values from DocumentComparison.ComparisonResults indicating whether there was a mismatch, and if so what kind.
    :param annotation1: [object] An instance of MentionLevelAnnotation.
    :param annotation2: [object] An optional second instance of mention level annotation. This value will be none if comparisonResult is "No Overlap".
    :param docLength: [int] The number of characters in the original note. Used in Analysis.Output.
    """
    def __init__(self, documentName, comparisonResult, annotation1, annotation2=None, docLength=None):
        # annotation2 may be None if comparisonType is "No Overlap", i.e. there is only one annotation to report, not a
        # pair of annotations.
        self.annotation1 = annotation1
        self.annotation2 = annotation2
        self.comparisonResult = comparisonResult
        self.docLength = docLength
        self.documentName = documentName

    @classmethod
    def CompareAllAnnotations(cls, document1, document2):
        """
        This function makes a list of all the annotations in both documents that do not have matches. It then reviews those lists to determine which discrepancies are due to class/attribute mismatches and which are due to non-overlapping spans. Finally, it returns a list of all the annotations along with their match or mismatch types as a list of `Comparison` objects.

        :param document1: [object] An instance of :class:`Document <eHostess.Annotations.Document.Document>`.
        :param document2: [object] A second instance of :class:`Document <eHostess.Annotations.Document.Document>`, whose source note is the same as document1.
        :return: [object] An instance of :class:`Comparison <eHostess.Analysis.DocumentComparison.Comparison>`, detailing the results of the comparison.
        """
        doc1Annotations = document1.annotations.values()
        doc2Annotations = document2.annotations.values()
        doc1Matches = [False] * len(document1.annotations)
        doc2Matches = [False] * len(document2.annotations)

        documentName = document1.documentName
        comparisons = []

        for index1, annotation1 in enumerate(doc1Annotations):
            if doc1Matches[index1]:
                continue
            for index2, annotation2 in enumerate(doc2Annotations):
                if doc2Matches[index2]:
                    continue

                # If there is a match set the corresponding indices in doc*Matches to True and break
                # Check overlap
                if MentionLevelAnnotation.overlap(annotation1, annotation2):
                    #Check annotation class.
                    if annotation1.annotationClass == annotation2.annotationClass:
                        #Check all attributes
                        if allAttributesMatch(annotation1, annotation2):
                            # We have a match!
                            doc1Matches[index1] = True
                            doc2Matches[index2] = True
                            comparisons.append(Comparison(documentName, ComparisonResults["5"], annotation1,
                                                          annotation2, docLength=document1.numberOfCharacters))
                            break

        doc1Mismatches = [a for index, a in enumerate(doc1Annotations) if not doc1Matches[index]]
        doc2Mismatches = [a for index, a in enumerate(doc2Annotations) if not doc2Matches[index]]

        processed2 = [False] * len(doc2Annotations)


        for index1, annotation1 in enumerate(doc1Mismatches):
            foundOverlap = False
            for index2, annotation2 in enumerate(doc2Mismatches):
                if processed2[index2]:
                    continue
                if MentionLevelAnnotation.overlap(annotation1, annotation2):
                    foundOverlap = True
                    processed2[index2] = True
                    if annotation1.annotationClass != annotation2.annotationClass:
                        # Class mismatch
                        if allAttributesMatch(annotation1, annotation2):
                            newComparison = cls(documentName, ComparisonResults["2"], annotation1, annotation2,
                                                 docLength=document1.numberOfCharacters)
                            comparisons.append(newComparison)
                        # Class and attribute mismatch
                        else:
                            newComparison = cls(documentName, ComparisonResults["4"], annotation1, annotation2,
                                                 docLength=document1.numberOfCharacters)
                            comparisons.append(newComparison)
                    # Attribute mismatch
                    else:
                        newComparison = cls(documentName, ComparisonResults["3"], annotation1, annotation2,
                                             docLength=document1.numberOfCharacters)
                        comparisons.append(newComparison)
            # No-overlap mismatch
            if not foundOverlap:
                newComparison = cls(documentName, ComparisonResults["1"], annotation1, docLength=document1.numberOfCharacters)
                comparisons.append(newComparison)

        for index, annotation2 in enumerate(doc2Mismatches):
            if processed2[index]:
                continue
            # No-overlap mismatch
            else:
                newComparison = cls(documentName, ComparisonResults["1"], annotation2, docLength=document1.numberOfCharacters)
                comparisons.append(newComparison)

        return comparisons


    @classmethod
    def CompareDocumentBatches(cls, batch1, batch2):
        """This method compares two sets of Documents. This method assumes that batch1 and batch2 contain the same number of documents and that the set of names in both batches is the same and that all names in a given batch are unique. It returns a dictionary keyed by the names of the documents where the values are an array of `Comparison` objects.

        :param batch1: [list of objects] A list of `Document` objects.
        :param batch2: [list of objects] A second list of `Document` objects.
        :return: [dict] A dictionary of `Comparison` arrays keyed by document name.
        """

        comparisons = {}

        sorted1 = sorted(batch1, key=lambda doc: doc.documentName)
        sorted2 = sorted(batch2, key=lambda doc: doc.documentName)

        for index, document in enumerate(sorted1):
            if sorted1[index].documentName != sorted2[index].documentName:
                raise RuntimeError("The batches were not sorted correctly or contain different documents.")

            comparisons[document.documentName] = Comparison.CompareAllAnnotations(sorted1[index], sorted2[index])

        return comparisons




    @classmethod
    def CompareDocClassAnnotations(cls, document1, document2, documentClassName="doc_classification"):
        """
        This method is not yet implemented.
        :param document1:
        :param document2:
        :param documentClassName:
        :return:
        """
        raise NotImplementedError("This method hasn't been implemented yet....but you can implement it if you want!")

