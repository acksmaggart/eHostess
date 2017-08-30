"""This module is intended to provide functions to consume Comparison objects and calculate arbitrary metrics."""

import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from eHostess.Analysis.DocumentComparison import ComparisonResults

def CalculateRecallPrecisionFScoreAndAgreement(comparisons, goldStandardPosition='first'):
    """
    This function calculates the recall, precision, F-score, and support of the two annotation groups represented by 'comparisons'. The policy for handling non-overlapping annotations is to consider all missing annotations as a negative test result, regardless of which group they are in.
    :param comparisons:
    :param goldStandardPosition: [string] Indicates which annotation in each comparison is the gold standard. Acceptable values are 'first' or 'second' to indicate that annotation1 or annotation2 should be used as the gold standard for all comparisons respectively.
    :return: [tuple (float, float, float, float)] A tuple containing the recall, precision, F-Score, (as decimal values) and agreement.
    """

    goldStandardResults = np.zeros(len(comparisons))
    testGroupResults = np.zeros(len(comparisons))
    agreementVec = np.zeros(len(comparisons))

    for index, comparison in enumerate(comparisons):
        goldStandardAnnotation = None
        testAnnotation = None
        if goldStandardPosition == 'first':
            goldStandardAnnotation = comparison.annotation1
            testAnnotation = comparison.annotation2
        if goldStandardPosition == 'second':
            goldStandardAnnotation = comparison.annotation2
            testAnnotation = comparison.annotation1

        # Determine agreement
        if comparison.comparisonResult == ComparisonResults["5"] or comparison.comparisonResult == ComparisonResults["6"]: #Match
            agreementVec[index] = 1

        # Since missing annotations are considered negative results no action needs to be taken for annotations that
        # are None since the np.arrays were initialized with zeros.
        if goldStandardAnnotation != None:
            if goldStandardAnnotation.annotationClass == "doc_classification":
                if goldStandardAnnotation.attributes["present_or_absent"] == "present":
                    goldStandardResults[index] = 1
            else:
                if goldStandardAnnotation.annotationClass == "bleeding_present":
                    goldStandardResults[index] = 1

        if testAnnotation != None:
            if testAnnotation.annotationClass == "doc_classification":
                if testAnnotation.attributes["present_or_absent"] == "present":
                    testGroupResults[index] = 1
            else:
                if testAnnotation.annotationClass == "bleeding_present":
                    testGroupResults[index] = 1

    precision, recall, fscore, support = precision_recall_fscore_support(goldStandardResults, testGroupResults, average='binary')
    agreement = float(np.sum(agreementVec)) / float(len(agreementVec))

    return recall, precision, fscore, agreement
