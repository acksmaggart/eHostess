"""
This class is meant to compare two Document objects and to report their discrepancies. A discrepancy is defined as
either of the following cases:
1. An annotation in one document does not overlap with any annotations in the other document.
2. An annotation in one document has class or attribute mismatches with all overalapping annotations in the other
document.

Implicitly then, a match is defined as a pair of annotations whose spans overlap and whose classes and attributes all
match. The algorithm implemented in this module assumes that if two annotations overlap and share their classes and all
attributes in common they are matches, even if there may be multiple overlapping annotations. This could also be a problem if
two annotators highlighted the same span which contained two different terms, and their intended term was different from
 the other annotator's intended term. This would produce a situation in which there were really two mismatches but it
 got recorded as a single match. This flaw was judged to be acceptable since the odds of its occurrence are low and the
 document-level classification is more important and immune to this possibility anyway.
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

DiscrepancyTypes ={
    "1" : "No Overlap",
    "2" : "Class Mismatch",
    "3" : "Attribute Mismatch",
    "4" : "Class and Attribute Mismatch"
    }

class Discrepancy:
    def __init__(self, discrepancyType, annotation1, annotation2=None):
        # annotation2 may be None if discrepancyType is "No Overlap", i.e. there is only one annotation to report, not a
        # pair of annotations.
        self.annotation1 = annotation1
        self.annotation2 = annotation2
        self.discrepancyType = discrepancyType

    @classmethod
    def DetectAllDiscrepancies(cls, document1, document2):
        """ This function makes a list of all the annotations in both documents that do not have matches. It then reviews
        those lists to determine which discrepancies are due to class/attribute mismatches and which are due to
        non-overlapping spans. Finally, it returns a list of Discrepancy objects."""
        doc1Annotations = document1.annotations.values()
        doc2Annotations = document2.annotations.values()
        doc1Matches = [False] * len(document1.annotations)
        doc2Matches = [False] * len(document2.annotations)

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
                            break

        doc1Mismatches = [a for index, a in enumerate(doc1Annotations) if not doc1Matches[index]]
        doc2Mismatches = [a for index, a in enumerate(doc2Annotations) if not doc2Matches[index]]

        processed2 = [False] * len(doc2Annotations)
        discrepancies = []

        for index1, annotation1 in enumerate(doc1Mismatches):
            foundOverlap = False
            for index2, annotation2 in enumerate(doc2Mismatches):
                if processed2[index2]:
                    continue
                if MentionLevelAnnotation.overlap(annotation1, annotation2):
                    foundOverlap = True
                    processed2[index2] = True
                    if annotation1.annotationClass != annotation2.annotationClass:
                        if allAttributesMatch(annotation1, annotation2):
                            newDiscrepancy = cls("Class Mismatch", annotation1, annotation2)
                            discrepancies.append(newDiscrepancy)
                        else:
                            newDiscrepancy = cls("Class and Attribute Mismatch", annotation1, annotation2)
                            discrepancies.append(newDiscrepancy)
                    else:
                        newDiscrepancy = cls("Attribute Mismatch", annotation1, annotation2)
                        discrepancies.append(newDiscrepancy)

            if not foundOverlap:
                newDiscrepancy = cls("No Overlap", annotation1)
                discrepancies.append(newDiscrepancy)

        for index, annotation2 in enumerate(doc2Mismatches):
            if processed2[index]:
                continue
            else:
                newDiscrepancy = cls("No Overlap", annotation2)
                discrepancies.append(newDiscrepancy)

        return discrepancies






#def DetectDocClassDiscrepancies(document1, document2, documentClassName="doc_classification"):

