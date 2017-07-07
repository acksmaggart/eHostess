"""
The purpose of this module is to produce human-readable output after conducting analysis. For example, converting
:class:`Comparison <eHostess.Analysis.DocumentComparison.Comparison>` objects to lines in a .csv file for review.
"""

from DocumentComparison import ComparisonResults

def ConvertComparisonsToTSV(comparisons, outputPath):
    """
    This function creates a TSV with a summary of the comparisons. Each line in the output file represents one :class:`Comparison <eHostess.Analysis.DocumentComparison.Comparison>` object. Specifically for each annotation comparison it will show the text highlighted by the two annotators or annotation methods, the type of agreement or disagreement, the span of the text, the annotator name, and the document length.

    This method encloses the text fields in quotes, assuming that any software used to parse the TSV file will know to ignore any tabs inside of quotes. It also assumes that the :class:`MentionLevelAnnotation <eHostess.Annotations.MentionLevelAnnotation.MentionLevelAnnotation>` objects contained in the comparisons all have a value for `annotator` and that all values of `annotator` belong to a set of size 2. In other words, there are only two different values for `annotator` and all annotation objects have exactly one of those two values. This function may not output the tsv file correctly if the annotation text contains both tab characters and double quotes.

    :param comparisons: [list of objects | object] A list of :class:`Comparison <eHostess.Analysis.DocumentComparison.Comparison>` objects or a single comparison object to output.
    :param outputPath: [string] The path specifying where to write the output TSV file.
    :return: None
    """

    if not isinstance(comparisons, list):
        comparisons = [comparisons]

    outFile = open(outputPath, 'w')
    comparisonWithTwoNamesHopefully = None
    # grabs a comparison instance with two annotations in order to get both annotator names. If all comparisons
    # contain only one annotation it grabs the last comparison
    for comparison in comparisons:
        comparisonWithTwoNamesHopefully = comparison
        if comparison.annotation2 != None:
            comparisonWithTwoNamesHopefully = comparison
            break
    firstName = comparisonWithTwoNamesHopefully.annotation1.annotator
    secondName = ""
    if comparisonWithTwoNamesHopefully.annotation2 != None:
        secondName = comparisonWithTwoNamesHopefully.annotation2.annotator
    outFile.write("DocumentName\t%sText\t%sText\tComparisonResult\tAgreement\t%s\t%s\tSpanStart\tSpanEnd\tDocLength\n" % (firstName, secondName, firstName, secondName))

    for comparison in comparisons:
        documentName = comparison.documentName
        annotationWithFirstName = None
        annotationWithSecondName = None
        if comparison.annotation1.annotator == firstName:
            annotationWithFirstName = comparison.annotation1
            annotationWithSecondName = comparison.annotation2
        else:
            annotationWithSecondName = comparison.annotation1
            annotationWithFirstName = comparison.annotation2

        # Text must be enclosed in quotes in case it contains tab characters.
        firstNameText = ""
        if annotationWithFirstName:
            firstNameText = '"' + annotationWithFirstName.text + '"'
        secondNameText = ""
        if annotationWithSecondName:
            secondNameText = '"' + annotationWithSecondName.text + '"'


        if comparison.comparisonResult == ComparisonResults["1"]: # No Overlap
            firstResult = ""
            secondResult = ""
            if annotationWithFirstName:
                if annotationWithFirstName.annotationClass == 'doc_classification':
                    firstResult = "DOC CLASS: " + str(annotationWithFirstName.attributes)
                else:
                    firstResult = annotationWithFirstName.annotationClass + str(annotationWithFirstName.attributes)

            elif annotationWithSecondName:
                if annotationWithSecondName.annotationClass == 'doc_classification':
                    secondResult = "DOC CLASS: " + str(annotationWithSecondName.attributes)
                else:
                    secondResult = annotationWithSecondName.annotationClass + str(annotationWithSecondName.attributes)
            else:
                raise RuntimeError("Either the first annotation or the second annotation should be non-null.")
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult,
                                                                    secondResult, comparison.annotation1.start,
                                                                    comparison.annotation1.end, comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["2"]: # Class mismatch
            firstResult = None
            secondResult = None
            if annotationWithFirstName.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotationWithFirstName.attributes)
                secondResult = "DOC CLASS: " + str(annotationWithSecondName.attributes)
            else:
                firstResult = annotationWithFirstName.annotationClass + str(annotationWithFirstName.attributes)
                secondResult = annotationWithSecondName.annotationClass + str(annotationWithSecondName.attributes)
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["3"]: # Attribute mismatch
            firstResult = None
            secondResult = None
            if annotationWithFirstName.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotationWithFirstName.attributes)
                secondResult = "DOC CLASS: " + str(annotationWithSecondName.attributes)
            else:
                firstResult = annotationWithFirstName.annotationClass + str(annotationWithFirstName.attributes)
                secondResult = annotationWithSecondName.annotationClass + str(annotationWithSecondName.attributes)
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["4"]: # Class and attribute mismatch
            firstResult = "Class: %s,  Attributes: %s" % (annotationWithFirstName.annotationClass,
                                                          annotationWithFirstName.attributes)
            secondResult = "Class: %s,  Attributes: %s" % (annotationWithSecondName.annotationClass,
                                                          annotationWithSecondName.attributes)

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["5"]: # Match
            firstResult = None
            secondResult = None
            if annotationWithFirstName.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotationWithFirstName.attributes)
                secondResult = "DOC CLASS: " + str(annotationWithSecondName.attributes)
            else:
                firstResult = annotationWithFirstName.annotationClass
                secondResult = annotationWithSecondName.annotationClass

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "1", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

    outFile.close()
    print "Done writing TSV file to %s" % outputPath
