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

    comparisonList = []
    for comparisonSublist in comparisons.values():
        comparisonList.extend(comparisonSublist)

    comparisons = comparisonList

    # Get the names of the annotators for each annotation group.
    name1 = ''
    name2 = ''
    foundNames = False
    for comparison in comparisons:
        if name1 != '' and name2 != '':
            foundNames = True
            break
        if name1 == '' and comparison.annotation1 != None:
            name1 = comparison.annotation1.annotator
        if name2 == '' and comparison.annotation2 != None:
            name2 = comparison.annotation1.annotator
    if not foundNames:
        raise RuntimeError("No names were found for either group of annotations.")

    #Prepare the column headers for the output file.
    outFile = open(outputPath, 'w')
    outFile.write("DocumentName\t%sText\t%sText\tComparisonResult\tAgreement\t%s\t%s\tSpanStart\tSpanEnd\tDocLength\n" % (name1, name2, name1, name2))

    for comparison in comparisons:
        documentName = comparison.documentName
        annotation1 = comparison.annotation1
        annotation2 = comparison.annotation2


        # Text must be enclosed in quotes in case it contains tab characters.
        firstNameText = ""
        if annotation1:
            firstNameText = '"' + annotation1.text + '"'
        secondNameText = ""
        if annotation2:
            secondNameText = '"' + annotation2.text + '"'


        if comparison.comparisonResult == ComparisonResults["1"]: # No Overlap
            firstResult = ""
            secondResult = ""

            spanStart = None
            spanEnd = None
            docLength = None

            if annotation1:
                if annotation1.annotationClass == 'doc_classification':
                    firstResult = "DOC CLASS: " + str(annotation1.attributes)
                else:
                    firstResult = annotation1.annotationClass + str(annotation1.attributes)

                spanStart = annotation1.start
                spanEnd = annotation1.end
                docLength = comparison.docLength

            elif annotation2:
                if annotation2.annotationClass == 'doc_classification':
                    secondResult = "DOC CLASS: " + str(annotation2.attributes)
                else:
                    secondResult = annotation2.annotationClass + str(annotation2.attributes)

                spanStart = annotation2.start
                spanEnd = annotation2.end
                docLength = comparison.docLength

            else:
                raise RuntimeError("Either the first annotation or the second annotation should be non-null.")

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult,
                                                                    secondResult, spanStart,
                                                                    spanEnd, docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["2"]: # Class mismatch
            firstResult = None
            secondResult = None
            if annotation1.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotation1.attributes)
                secondResult = "DOC CLASS: " + str(annotation2.attributes)
            else:
                firstResult = annotation1.annotationClass + str(annotation1.attributes)
                secondResult = annotation2.annotationClass + str(annotation2.attributes)
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["3"]: # Attribute mismatch
            firstResult = None
            secondResult = None
            if annotation1.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotation1.attributes)
                secondResult = "DOC CLASS: " + str(annotation2.attributes)
            else:
                firstResult = annotation1.annotationClass + str(annotation1.attributes)
                secondResult = annotation2.annotationClass + str(annotation2.attributes)
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["4"]: # Class and attribute mismatch
            firstResult = "Class: %s,  Attributes: %s" % (annotation1.annotationClass,
                                                          annotation1.attributes)
            secondResult = "Class: %s,  Attributes: %s" % (annotation2.annotationClass,
                                                          annotation2.attributes)

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "0", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

        if comparison.comparisonResult == ComparisonResults["5"]: # Match
            firstResult = None
            secondResult = None
            if annotation1.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + str(annotation1.attributes)
                secondResult = "DOC CLASS: " + str(annotation2.attributes)
            else:
                firstResult = annotation1.annotationClass
                secondResult = annotation2.annotationClass

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, firstNameText, secondNameText, comparison.comparisonResult,
                                                                    "1", firstResult, secondResult,
                                                                    comparison.annotation1.start,
                                                                    comparison.annotation1.end,
                                                                    comparison.docLength))
            continue

    outFile.close()
    print "Done writing TSV file to %s" % outputPath
