"""
The purpose of this module is to produce human-readable output after conducting analysis. For example, converting
`Discrepancy` objects to lines in a .csv file for review.
"""

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
    outFile.write("Method1\tText1\tMethod2\tText2\t")
    for discrepancy in discrepancies:


    outFile.close()
