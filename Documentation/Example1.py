from eHostess.PyConTextInterface.PyConText import PyConTextInterface
from eHostess.PyConTextInterface.SentenceSplitters import TargetSpanSplitter
import pyConTextNLP.itemData as itemData
from eHostess.eHostInterface.KnowtatorReader import KnowtatorReader
from eHostess.Analysis.DocumentComparison import Comparison
import eHostess.Analysis.Metrics as Metrics
from eHostess.Analysis.Output import ConvertComparisonsToTSV
from eHostess.MongoDBInterface import MongoTools

# Specify the paths to the directories that contain the notes to be annotated by PyConText
noteDirectories = ['./path/to/dir1/corpus/', './path/to/dir2/corpus/']

# Process the notes using an included sentence splitter, in this case we will use the target-span splitter, which
# divides an input document up into sentences by first identifying target terms in the document and then capturing a
# configurable number of words on either side of the target term. In this case we will capture the target term, the
# ten words before the term, and the six words after the term as a single string. This will be performed on all the
# input notes.
targetsForSpanSplitter = itemData.instantiateFromCSVtoitemData('./path/to/targets.tsv')
pyConTextInputObject = TargetSpanSplitter.splitSentencesMultipleDocuments(noteDirectories, targetsForSpanSplitter, 10, 6)

# The following line executes PyConText using the default Targets and Modifiers found in
# eHostess/PyConTextInterface/TargetsAndModifiers. The user may specify a different location using the method's options.
DocumentsAnnotatedByPyConText = PyConTextInterface.PerformAnnotation(pyConTextInputObject)

# Now bring in the human annotation by first reading the eHost .knowtator files:
knowtatorFileDirectories = ['./path/to/dir1/saved/', './path/to/dir2/saved/']
DocumentsAnnotatedInEHost = KnowtatorReader.parseMultipleKnowtatorFiles(knowtatorFileDirectories)

# Compare the two sets of annotations, optionally specifying which classes are equivalent. See the documentation for
# other configuration options:
comparisonResults = Comparison.CompareDocumentBatches(DocumentsAnnotatedByPyConText,
                                                      DocumentsAnnotatedInEHost,
                                                      equivalentClasses=[["present", "positive"], ["absent", "negative"]])

# Print the comparison result metrics:
print Metrics.CalculateRecallPrecisionFScoreAndAgreement(comparisonResults)

# Output the results to a TSV file for review:
ConvertComparisonsToTSV(comparisonResults, '/path/to/output.tsv')

# Save the annotations to a backing MongoDB store:
MongoTools.InsertMultipleDocuments(DocumentsAnnotatedByPyConText, "Name of current annotation round")
MongoTools.InsertMultipleDocuments(DocumentsAnnotatedInEHost, "Name of current annotation round")

