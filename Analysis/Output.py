"""
The purpose of this module is to produce human-readable output after conducting analysis. For example, converting
`Discrepancy` objects to lines in a .csv file for review.
"""

from DetectDiscrepancies import DiscrepancyTypes

def ConvertDiscrepanciesToCSV(discrepancies, outputPath):
    """This function creates a CSV file using tabs as the delimiter. It encloses the text fields in quotes, assuming
    that any software used to parse the CSV file will know to ignore any tabs inside of quotes. It also assumes
    that the reader would rather see the text highlighted by the human rather than the whole sentence. It also assumes
    that the `MentionLevelAnnotation` objects contained in the discrepancies all have a value for `annotator` and that
    all values of `annotator` belong to a set of size 2. In other words, there are only two different values for
    `annotator` and all annotation objects have exactly one of those two values."""
    if not isinstance(discrepancies, list):
        discrepancies = [discrepancies]

    outFile = open(outputPath, 'w')
    discrepancyWithTwoNamesHopefully = None
    # grabs a discrepancy instance with two annotations in order to get both annotator names. If all discrepancies
    # contain only one annotation it grabs the last discrepancy
    for discrepancy in discrepancies:
        discrepancyWithTwoNamesHopefully = discrepancy
        if discrepancy.annotation2 != None:
            discrepancyWithTwoNamesHopefully = discrepancy
            break
    firstName = discrepancyWithTwoNamesHopefully.annotation1.annotator
    secondName = ""
    if discrepancyWithTwoNamesHopefully.annotation2 != None:
        secondName = discrepancyWithTwoNamesHopefully.annotation2.annotator
    outFile.write("DocumentName\tText\tMismatchType\t%s\t%s\tSpanStart\tSpanEnd\tDocLength\n" % (firstName, secondName))

    for discrepancy in discrepancies:
        documentName = discrepancy.documentName
        annotationWithFirstName = None
        annotationWithSecondName = None
        if discrepancy.annotation1.annotator == firstName:
            annotationWithFirstName = discrepancy.annotation1
            annotationWithSecondName = discrepancy.annotation2
        else:
            annotationWithSecondName = discrepancy.annotation1
            annotationWithFirstName = discrepancy.annotation2

        # Get the text, giving preference to the human annotation when present.
        text = None
        if not annotationWithFirstName:
            text = annotationWithSecondName.text
        elif not annotationWithSecondName:
            text = annotationWithFirstName.text
        elif annotationWithFirstName.annotator != "pyConTextNLP":
            text = annotationWithFirstName.text
        else:
            text = annotationWithSecondName.text

        if discrepancy.discrepancyType == DiscrepancyTypes["1"]: # No Overlap
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, text, discrepancy.discrepancyType,
                                                          annotationWithFirstName.annotationClass, "",
                                                          discrepancy.annotation1.start, discrepancy.annotation1.end,
                                                          discrepancy.docLength))
            continue

        if discrepancy.discrepancyType == DiscrepancyTypes["2"]: # Class mismatch
            firstResult = annotationWithFirstName.annotationClass
            secondResult = annotationWithSecondName.annotationClass

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, text, discrepancy.discrepancyType, firstResult, secondResult,
                                                          discrepancy.annotation1.start, discrepancy.annotation1.end,
                                                          discrepancy.docLength))
            continue

        if discrepancy.discrepancyType == DiscrepancyTypes["3"]: # Attribute mismatch
            firstResult = None
            secondResult = None
            if annotationWithFirstName.annotationClass == 'doc_classification':
                firstResult = "DOC CLASS: " + annotationWithFirstName.attributes["present_or_absent"]
                secondResult = "DOC CLASS: " + annotationWithSecondName.attributes["present_or_absent"]
            else:
                firstResult = str(annotationWithFirstName.attributes)
                secondResult = str(annotationWithSecondName.attributes)
            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, text, discrepancy.discrepancyType, firstResult, secondResult,
                                                          discrepancy.annotation1.start, discrepancy.annotation1.end,
                                                          discrepancy.docLength))
            continue

        if discrepancy.discrepancyType == DiscrepancyTypes["4"]: # Class and attribute mismatch
            firstResult = "Class: %s,  Attributes: %s" % (annotationWithFirstName.annotationClass,
                                                          annotationWithFirstName.attributes)
            secondResult = "Class: %s,  Attributes: %s" % (annotationWithSecondName.annotationClass,
                                                          annotationWithSecondName.attributes)

            outFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (documentName, text, discrepancy.discrepancyType, firstResult, secondResult,
                                                          discrepancy.annotation1.start, discrepancy.annotation1.end,
                                                          discrepancy.docLength))
            continue

    outFile.close()
