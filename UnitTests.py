import glob

#### Test Preprocessing. ####
import eHostess.NotePreprocessing.Preprocessor as preprocessor

print "Testing Preprocesssor duplicate detection."
dirList = ['./NotePreprocessing/testCorpus/*', './NotePreprocessing/testCorpus2/*']
duplicateProcessor = preprocessor.DuplicateProcessor(dirList)

duplicateProcessor.findDuplicates()
numSubsets = len(duplicateProcessor.subsetsToRemove)
numDuplicates = len(duplicateProcessor.exactDuplicatesToRemove)
numUnion = len(duplicateProcessor._getUnionOfDuplicatesAndSubsets())

if numSubsets == 3 and numDuplicates == 4 and numUnion == 6:
    print "Passed\n"
else:
    print '*****************Test Failed***************************'
# duplicateProcessor.reportDuplicates()


#### Test eHostInterface.KnowtatorReader.getOriginalFileLength() ####
from eHostess.eHostInterface.KnowtatorReader import getOriginalFileLength
failed = False
print "Testing eHostInterface.KnowtatorReader.getOriginalFileLength()"

length = getOriginalFileLength('./UnitTestDependencies/eHostInterface/OriginalLengthandParseSingle/saved/2530.txt.knowtator.xml',
                               None)
if length != 8442:
    failed = True

length = getOriginalFileLength(
    './UnitTestDependencies/eHostInterface/OriginalLengthandParseSingle/saved/2530.txt.knowtator.xml',
    './UnitTestDependencies/eHostInterface/OriginalLengthandParseSingle/corpus')
if length != 8442:
    failed = True

if failed:
    print '*****************Test Failed***************************'
else:
    print "Passed\n"


#### Test eHostInterface.KnowtatorReader.parseSingleKnowtatorFile() ####
from eHostess.eHostInterface.KnowtatorReader import KnowtatorReader
failed = False
print "Testing eHostInterface.KnowtatorReader.parseSingleKnowtatorFile()"

document = KnowtatorReader.parseSingleKnowtatorFile('./UnitTestDependencies/eHostInterface/OriginalLengthandParseSingle/saved/2530.txt.knowtator.xml')

if document.numberOfCharacters != 8442 \
    or len(document.annotations) != 1 \
    or document.annotations.values()[0].attributes["present_or_absent"] != 'absent' \
    or document.documentName != '2530' \
    or document.annotations.values()[0].annotationClass != 'doc_classification' \
    or document.annotations.values()[0].annotationId != 'EHOST_Instance_438' \
    or document.annotations.values()[0].annotator != 'Shane':
    failed = True

if failed:
    print '*****************Test Failed***************************'
else:
    print "Passed\n"


#### Test path cleaner, turns path strings into glob-able directory strings. ####
from eHostess.Utilities.utilities import cleanDirectoryList as cleaner

print 'Testing Utilities.cleanDirectoryList()'
dirs = ['/Some/path/to/stuff', '/Some/path/to/stuff/', '/Some/path/to/stuff/*']
cleanDirs = cleaner(dirs)
failed = False
for dirName in cleanDirs:
    if dirName != '/Some/path/to/stuff/*':
        print '*****************Test Failed***************************'
        failed = True
if not failed:
    print 'Passed\n'

#### Test annotation overlap MentionLevelAnnotation.overlap() ####
print 'Testing MentionLevelAnnotation.overlap()'
failed = False
from Annotations.MentionLevelAnnotation import MentionLevelAnnotation

annotation1 = MentionLevelAnnotation("annotation 1 text", 0, 0, "annotator1", "annotator1 ID", {})
annotation2 = MentionLevelAnnotation("annotation 2 text", 10, 20, "annotator1", "annotator1 ID", {})

# case 1: same span
annotation1.start = 10
annotation1.end = 20
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 2:
annotation1.start = 10
annotation1.end = 15
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 3:
annotation1.start = 15
annotation1.end = 20
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 4:
annotation1.start = 0
annotation1.end = 5
if MentionLevelAnnotation.overlap(annotation1, annotation2) != False:
    failed = True

# case 5:
annotation1.start = 0
annotation1.end = 10
if MentionLevelAnnotation.overlap(annotation1, annotation2) != False:
    failed = True

# case 6:
annotation1.start = 0
annotation1.end = 15
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 7:
annotation1.start = 12
annotation1.end = 17
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 8:
annotation1.start = 15
annotation1.end = 25
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True

# case 9:
annotation1.start = 20
annotation1.end = 25
if MentionLevelAnnotation.overlap(annotation1, annotation2) != False:
    failed = True

# case 10:
annotation1.start = 25
annotation1.end = 30
if MentionLevelAnnotation.overlap(annotation1, annotation2) != False:
    failed = True

# case 11:
annotation1.start = 5
annotation1.end = 25
if MentionLevelAnnotation.overlap(annotation1, annotation2) != True:
    failed = True


if failed:
    print '*****************Test Failed***************************'
else:
    print 'Passed\n'


#### Test PyConTextInterface.SentenceReconstructor ####
from PyConTextInterface.SentenceReconstructor import SentenceReconstuctor as Reconstructor
from pyConTextNLP.helpers import sentenceSplitter as Splitter
print 'Testing PyConTextInterface.SentenceReconstructor.SentenceReconstructor()'

infile = open('./UnitTestDependencies/SentenceReconstructor/11.txt', 'r')
noteBody1 = infile.read()
infile.close()
infile = open('./UnitTestDependencies/SentenceReconstructor/12.txt', 'r')
noteBody2 = infile.read()
infile.close()

reconstructor = Reconstructor()

failed = False
for note in [noteBody1, noteBody2]:
    reconstructor.startNewNote(note)
    sentences = Splitter().splitSentences(note)
    reconstructedNote = ""
    for sentence in sentences:
        reconstructedNote += reconstructor.reconstructSentence(sentence)
    if reconstructedNote != note:
        failed = True
        break
if failed:
    print '*****************Test Failed***************************'
else:
    print 'Passed\n'

#### Test PyConTextInterface.PyConText.AnnotateSingleDocument() ####
print 'Testing PyConTextInterface.PyConText.AnnotateSingleDocument()'
from eHostess.PyConTextInterface.PyConText import PyConTextInferface

failed = False

gotException = False
try:
    contradictoryDoc = PyConTextInferface.AnnotateSingleDocument('./UnitTestDependencies/PyConText/AnnotateSingleDocument/TestAffirmedAndNegatedInSameSentence.txt')
except RuntimeError as error:
    gotException = True
if not gotException:
    failed = True

document = PyConTextInferface.AnnotateSingleDocument('./UnitTestDependencies/PyConText/AnnotateSingleDocument/testDoc.txt')
spans = [(69, 74), (148, 153), (242, 247)]
classifications = ["bleeding_present", "bleeding_absent", "bleeding_present"]
for index, annotation in enumerate(document.annotations.values()):
    if annotation.start != spans[index][0] or annotation.end != spans[index][1] \
            or classifications[index] != annotation.annotationClass:
        failed = True

if failed:
    print '*****************Test Failed***************************'
else:
    print 'Passed\n'


#### Test PyConTextInterface.PyConText.AnnotateMultipleDocuments() ####
print 'Testing PyConTextInterface.PyConText.AnnotateMultipleDocuments()'
from eHostess.PyConTextInterface.PyConText import PyConTextInferface

failed = False

directories = glob.glob('./UnitTestDependencies/PyConText/AnnotateMultipleDocuments/*')

document = PyConTextInferface.AnnotateSingleDocument('./UnitTestDependencies/PyConText/AnnotateSingleDocument/testDoc.txt')

doc1spans = [(69, 74), (148, 153), (242, 247)]
doc1classifications = ["bleeding_present", "bleeding_absent", "bleeding_present"]

doc2spans = [(72, 77), (166, 171), (242, 247)]
doc2classifications = ["bleeding_absent", "bleeding_present", "bleeding_present"]

doc3spans = [(84, 89), (160, 165), (239, 244)]
doc3classifications = ["bleeding_present", "bleeding_present", "bleeding_absent"]

doc4spans = [(69, 74), (160, 165), (239, 244)]
doc4classifications = ["bleeding_present", "bleeding_present", "bleeding_absent"]

doc5spans = [(72, 77), (151, 156), (242, 247)]
doc5classifications = ["bleeding_absent", "bleeding_present", "bleeding_present"]

doc6spans = [(84, 89), (163, 168), (242, 247)]
doc6classifications = ["bleeding_present", "bleeding_absent", "bleeding_present"]

allSpans = [doc1spans, doc2spans, doc3spans, doc4spans, doc5spans, doc6spans]
allClassifications = [doc1classifications, doc2classifications, doc3classifications, doc4classifications,
                   doc5classifications, doc6classifications]

documents = PyConTextInferface.AnnotateMultipleDocuments(directories)
for docIndex, document in enumerate(documents):
    spans = allSpans[docIndex]
    classifications = allClassifications[docIndex]
    for index, annotation in enumerate(document.annotations.values()):
        if annotation.start != spans[index][0] or annotation.end != spans[index][1] \
                or classifications[index] != annotation.annotationClass:
            failed = True

if failed:
    print '*****************Test Failed***************************'
else:
    print 'Passed\n'

    #### Test PyConTextInterface.PyConText.AnnotateSingleDocument() ####
    print 'Testing PyConTextInterface.PyConText.AnnotateSingleDocument()'
    from eHostess.PyConTextInterface.PyConText import PyConTextInferface

    failed = False

    gotException = False
    try:
        contradictoryDoc = PyConTextInferface.AnnotateSingleDocument(
            './UnitTestDependencies/PyConText/AnnotateSingleDocument/TestAffirmedAndNegatedInSameSentence.txt')
    except RuntimeError as error:
        gotException = True
    if not gotException:
        failed = True

    document = PyConTextInferface.AnnotateSingleDocument(
        './UnitTestDependencies/PyConText/AnnotateSingleDocument/testDoc.txt')
    spans = [(69, 74), (148, 153), (242, 247)]
    classifications = ["bleeding_present", "bleeding_absent", "bleeding_present"]
    for index, annotation in enumerate(document.annotations.values()):
        if annotation.start != spans[index][0] or annotation.end != spans[index][1] \
                or classifications[index] != annotation.annotationClass:
            failed = True

    if failed:
        print '*****************Test Failed***************************'
    else:
        print 'Passed\n'

    #### Test Analysis.Output.ConvertDiscrepanciesToCSV() ####
    print 'Testing Analysis.Output.ConvertDiscrepanciesToCSV()'
    from eHostess.Analysis.Output import ConvertDiscrepanciesToCSV
    from eHostess.Analysis.DetectDiscrepancies import Discrepancy

    failed = False

    doc1 = KnowtatorReader.parseSingleKnowtatorFile(
        './UnitTestDependencies/Output/DiscrepanciesToCSV/annotator1/saved/2530.txt.knowtator.xml')
    doc2 = KnowtatorReader.parseSingleKnowtatorFile(
        './UnitTestDependencies/Output/DiscrepanciesToCSV/annotator2/saved/2530.txt.knowtator.xml')

    discrepancies = Discrepancy.DetectAllDiscrepancies(doc1, doc2)
    ConvertDiscrepanciesToCSV(discrepancies, '../output/discrepancies.txt')

    if failed:
        print '*****************Test Failed***************************'
    else:
        print 'Passed\n'
