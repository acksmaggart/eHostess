from eHostess.PyConTextInterface.PyConText import PyConTextInterface
from eHostess.eHostInterface.KnowtatorReader import KnowtatorReader
from eHostess.Analysis.DocumentComparison import Comparison
from eHostess.Analysis.Output import ConvertComparisonsToTSV

# Annotate using PyConText:
noteDirectories = ['./path/to/dir1/corpus/', './path/to/dir2/corpus/']
# The following line executes PyConText using the default Targets and Modifiers found in
# eHostess/PyConTextInterface/TargetsAndModifiers, and using the built-in PyConText sentence splitter.
# Feel free to modify the default targets, modifiers, and sentence splitter, or provide your own using
# the optional parameters.
DocumentsAnnotatedByPyConText = PyConTextInterface.AnnotateMultipleDocuments(noteDirectories)

# Read human-produced annotations from eHost:
knowtatorFileDirectories = ['./path/to/dir1/saved/', './path/to/dir2/saved/']
DocumentsAnnotatedInEHost = KnowtatorReader.parseMultipleKnowtatorFiles(knowtatorFileDirectories)

# Compare the two sets of annotations:
comparisonResults = Comparison.CompareDocumentBatches(DocumentsAnnotatedByPyConText, DocumentsAnnotatedInEHost)

# Output the results to a TSV file:
ConvertComparisonsToTSV(comparisonResults, '/path/to/output.tsv')

