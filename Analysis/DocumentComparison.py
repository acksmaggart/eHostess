"""
This module is designed to compare two documents, or two sets of documents, and to report the annotations that do or do not match between corresponding documents.
"""

from ..Annotations.Document import Document
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
import numpy as np
from sklearn.metrics import precision_recall_fscore_support


def allAttributesMatch(annotation1, annotation2):
    if len(annotation1.attributes) != len(annotation2.attributes):
        return False

    for attribKey1 in annotation1.attributes:
        if attribKey1 not in annotation2.attributes:
            return False
        if annotation1.attributes[attribKey1] != annotation2.attributes[attribKey1]:
            return False

    return True

def classesMatch(annotation1, annotation2, equivalentClasses):
    """Checks if the classes match, considering 'equivalentClasses' and returns a boolean."""
    if equivalentClasses == None:
        if annotation1.documentClass == annotation2.documentClass:
            return True
        else:
            return False
    else:
        for sublist in equivalentClasses:
            if annotation1.documentClass in sublist and annotation2.documentClass in sublist:
                return True
        return False

def attributesMatch(annotation1, annotation2, ignoreAttributes):
    """Checks if the attributes match, considering 'ignoreAttributes' and returns a boolean."""
    if ignoreAttributes:
        return True
    else:
        return allAttributesMatch(annotation1, annotation2)

ComparisonResults ={
    "1" : "No Overlap",
    "2" : "Class Mismatch",
    "3" : "Attribute Mismatch",
    "4" : "Class and Attribute Mismatch",
    "5" : "Match"
    }

class Comparison:
    """
    Instances of the Comparison class represent the result of comparing two related MentionLevelAnnotation objects. Depending on whether or not the two annotation are the same the result of the comparison may be a match or a mismatch. If the annotations do not match then the resulting Comparison object will contain information about the dicrepancy between the two annotations. A discrepancy is defined as either of the following cases:
    1. An annotation in one document does not overlap with any annotations in the other document.
    2. An annotation in one document has class or attribute mismatches with all overalapping annotations in the other document.

    Implicitly then, a match is defined as a pair of annotations whose spans overlap and whose classes and attributes all match.

    In order to facilitate the calculation of metrics using the comparison objects produced by this class the methods of this class ensure that whichever document or group of documents was passed as 'document1' to CompareAllAnnotations or as 'batch1' to CompareDocumentBatches will be passed as 'annotation1' to the Comparison class initializer. The same is true for the document or documents passed as the second argument to CompareAllAnnotations or CompareDocumentBatches. e.g. when comparing a group of annotations produces using a gold-standard method to a group of annotation produced using a new method, if the user passes the gold-standard annotations as the first argument to CompareAllAnnotations then all the Comparison objects produced will have an annotation from the gold-standard group as annotation1 and an annotation from the new method as annotation2. In cases of non-overlapping annotations there will be a 'None' value in place of the missing annotation.

    The algorithm implemented in this module assumes that if two annotations overlap and share their classes and all attributes in common they are matches, even if there may be multiple overlapping annotations. This could be a problem if two annotators highlighted the same span which contained two different terms, and their intended term was different from the other annotator's intended term. This would produce a situation in which there were really two mismatches but it got recorded as a single match. This flaw was judged to be acceptable since the odds of its occurrence are low and the document-level classification is more important and fairly immune to this possibility anyway. The second case that will produce an errant result is if there are multiple terms in quick succession and one annotator highlights them all as a single annotation while the other annotates each one individually. The first annotation created by the second annotator will match the first annotator's long annotation and the rest of the smaller annotations will show up as non-overlapping mismatches. This is of course not desirable, however, it has yet to be determined if it constitutes a problem worth fixing.

    :param documentName: [string] Typically a user wishes to compare two sets of annotations produced from the same note. This parameter is the name of that note.
    :param comparisonResult: [string] One of the values from the DocumentComparison.ComparisonResults dict indicating whether there was a mismatch, and if so what kind.
    :param annotation1: [object] An instance of MentionLevelAnnotation from the document or document groups entered as the first argument to CompareAllAnnotations or CompareDocumentBatches, May be None if there is no overlap.
    :param annotation2: [object] An instance of MentionLevelAnnotation from the document or document groups entered as the second argument to CompareAllAnnotations or CompareDocumentBatches, May be None if there is no overlap.
    :param docLength: [int] The number of characters in the original note. Used in Analysis.Output.
    """
    def __init__(self, documentName, comparisonResult, annotation1, annotation2, docLength=None):
        # in cases of non-overlapping annotations either annotation1 or annotation 2 may be None depending on
        # which annotation group was missing an annotation.
        self.annotation1 = annotation1
        self.annotation2 = annotation2
        self.comparisonResult = comparisonResult
        self.docLength = docLength
        self.documentName = documentName

    @classmethod
    def CompareAllAnnotations(cls, document1, document2, equivalentClasses=None, ignoreAttributes=False):
        """
        This function compares the annotation objects contained in two Document or ClassifiedDocument instances. It first makes a list of all the annotations in both documents that do not have matches (see the Comparison class doc_string for more information about what constitutes a match). It then reviews those lists to determine which discrepancies are due to class/attribute mismatches and which are due to non-overlapping spans. Finally, it returns a list of all the annotations along with their match or mismatch types as a list of `Comparison` objects.

        :param document1: [object] An instance of :class:`Document <eHostess.Annotations.Document.Document>`.
        :param document2: [object] A second instance of :class:`Document <eHostess.Annotations.Document.Document>`, whose source note is the same as document1.
        :param equivalentClasses:[ list of lists] If None (default) this method will only consider annotation to be matching if they have the same 'annotationClass' attribute. However, the user may include a list of lists, specifying which classes are equivalent and should be considered a match anyway. For example, the user may have produced annotations using the following four classes: 'condition_present', 'condition_likely', 'condition_absent', 'condition_hypothetical'. If 'equivalentClasses' is None, 'condition_present' annotations will only match other 'condition_present' annotations, 'condition_likely' annotations will only math other 'condition_likely' annotations, etc. However, the user may wish to group class labels into meta-classes, so to speak, and consider both 'condition_present' and 'condition_likely' annotations as the same class and 'condition_absent' and 'condition_hypothetical' as the same class. In this case the user would pass the list [['condition_present', 'condition_likely'],['condition_absent', 'condition_hypothetical']] as the value of 'equivalentClasses' and all annotation pairs whose classes are in the same sublist will be considered a match.
        :param ignoreAttributes: [bool] If False, default, this method compares all the attributes between the annotations contained in the input documents. Only counting annotations as a match if they share attributes and attribute values. See MentionLevelAnnotation for more information about the concept of attributes.
        :return: [object] An instance of :class:`Comparison <eHostess.Analysis.DocumentComparison.Comparison>`, detailing the results of the comparison.
        """
        doc1Annotations = document1.annotations
        doc2Annotations = document2.annotations
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
                    if classesMatch(annotation1, annotation2, equivalentClasses):
                        #Check all attributes
                        if attributesMatch(annotation1, annotation2, ignoreAttributes):
                            # We have a match!
                            doc1Matches[index1] = True
                            doc2Matches[index2] = True
                            comparisons.append(Comparison(documentName, ComparisonResults["5"], annotation1,
                                                          annotation2, docLength=document1.numberOfCharacters))
                            break

        doc1Mismatches = [a for index, a in enumerate(doc1Annotations) if not doc1Matches[index]]
        doc2Mismatches = [a for index, a in enumerate(doc2Annotations) if not doc2Matches[index]]

        processed2 = [False] * len(doc2Annotations)

        # Now consider all the annotations that did not have a match and determine which type of mismatch they are.
        for index1, annotation1 in enumerate(doc1Mismatches):
            foundOverlap = False
            for index2, annotation2 in enumerate(doc2Mismatches):
                if processed2[index2]:
                    continue
                if MentionLevelAnnotation.overlap(annotation1, annotation2):
                    foundOverlap = True
                    processed2[index2] = True
                    if not classesMatch(annotation1, annotation2, equivalentClasses):
                        # Class mismatch
                        if attributesMatch(annotation1, annotation2, ignoreAttributes):
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
                newComparison = cls(documentName, ComparisonResults["1"], annotation1, None, docLength=document1.numberOfCharacters)
                comparisons.append(newComparison)

        for index, annotation2 in enumerate(doc2Mismatches):
            if processed2[index]:
                continue
            # No-overlap mismatch
            else:
                newComparison = cls(documentName, ComparisonResults["1"], None, annotation2, docLength=document1.numberOfCharacters)
                comparisons.append(newComparison)

        return comparisons


    @classmethod
    def CompareDocumentBatches(cls, batch1, batch2):
        """This method compares the annotations contained in two sets of Documents. This method assumes that batch1 and batch2 contain the same number of documents and that the set of names in both batches is the same and that all names in a given batch are unique. It returns a list of `Comparison` objects.

        :param batch1: [list of objects] A list of `Document` objects.
        :param batch2: [list of objects] A second list of `Document` objects.
        :return: [list] A list of `Comparison` arrays keyed by document name.
        """

        comparisons = []

        sorted1 = sorted(batch1, key=lambda doc: doc.documentName)
        sorted2 = sorted(batch2, key=lambda doc: doc.documentName)

        for index, document in enumerate(sorted1):
            if sorted1[index].documentName != sorted2[index].documentName:
                print "Batch 1:"
                docList1 = [document.documentName for document in sorted1]
                print docList1
                print len(docList1)

                print "Batch 2:"
                docList2 = [document.documentName for document in sorted2]
                print len(docList2)

                raise RuntimeError("The batches were not sorted correctly or contain different documents.")

            comparisons.extend(Comparison.CompareAllAnnotations(sorted1[index], sorted2[index]))

        return comparisons

    @classmethod
    def CalculateTestMetricsForDocumentClassifications(cls, classifiedDocumentsGoldStandard, classifiedDocumentsTestGroup, positiveClass="positive"):
        """
        This method takes two lists of ClassifiedDocument objects, presumably produced using different annotation methods, and compares the document classification labels in the test group to the gold standard labels. It calculates and returns the recall, precision, f-score, and agreement between the two groups. Agreement in this case is defined as the percentage of labels that are the same between the two groups regardless of label value. Currently this method only supports binary classification schemes, with the positive class identified by the 'positiveClass' argument. Any class label not matching the value of 'positiveClass' will be considered negative. If the names of the documents in the gold standard group do not match the names of the documents in the test group this method will produce a RuntimeError.

        :param classifiedDocumentsGoldStandard: [list of objects] A list of ClassifiedDocument objects whose document classification labels will serve as the comparison standard.
        :param classifiedDocumentsTestGroup: [list of objects] A list of ClassifiedDocument objects whose classification labels will be compared to the gold standard labels.
        :param positiveClass: [string] A string identifying which classification label in the document groups should be considered the positive label in calculating the recall, precision, and f score.
        :return: [tuple] A four-tuple of the form (recall, precision, f-score, agreement) all of which are decimal values.
        """
        if len(classifiedDocumentsGoldStandard) != len(classifiedDocumentsTestGroup):
            raise RuntimeError("The classifiedDocumentsGoldStandard list must contain the same number of documents as the classifiedDocumentsTestGroup list, as currently implemented they are not the same length.")
        classifiedDocumentsGoldStandard.sort(key=lambda x: x.documentName)
        classifiedDocumentsTestGroup.sort(key=lambda x: x.documentName)

        for index in range(len(classifiedDocumentsGoldStandard)):
            if classifiedDocumentsGoldStandard[index].documentName != classifiedDocumentsTestGroup[index].documentName:
                print "Gold Standard list:"
                for doc in classifiedDocumentsGoldStandard:
                    print doc.documentName
                print "\n\nTest Group list:"
                for doc in classifiedDocumentsTestGroup:
                    print doc.documentName
                raise RuntimeError("The names of the documents in classifiedDocumentsGoldStandard must be the same as the names in the classifiedDocumentsTestGroup. The names have been printed above for convenience.")

        agreementVec = np.zeros(len(classifiedDocumentsGoldStandard))
        goldStandardPositiveVec = np.zeros(len(classifiedDocumentsGoldStandard))
        testGroupPositiveVec = np.zeros(len(classifiedDocumentsGoldStandard))

        for index in range(len(classifiedDocumentsGoldStandard)):
            if classifiedDocumentsGoldStandard[index].documentClass == positiveClass:
                goldStandardPositiveVec[index] = 1
            if classifiedDocumentsTestGroup[index].documentClass == positiveClass:
                testGroupPositiveVec[index] = 1
            if classifiedDocumentsGoldStandard[index].documentClass == classifiedDocumentsTestGroup[index].documentClass:
                agreementVec[index] = 1

        agreement = float(np.sum(agreementVec))/float(len(agreementVec))
        recall, precision, fscore, support = precision_recall_fscore_support(goldStandardPositiveVec, testGroupPositiveVec, average="binary")

        return recall, precision, fscore, agreement

