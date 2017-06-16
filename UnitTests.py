
#### Test Preprocessing. ####
import NotePreprocessing.Preprocessor as preprocessor

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


#### Test path cleaner, turns path strings into glob-able directory strings. ####
from NotePreprocessing.Preprocessor import cleanDirectoryList as cleaner

print 'Testing Preprocessor.cleanDirectoryList()'
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

annotation1 = MentionLevelAnnotation("doc1", "annotation 1 text", 0, 0, "annotator1", "annotator1 ID", {})
annotation2 = MentionLevelAnnotation("doc2", "annotation 2 text", 10, 20, "annotator1", "annotator1 ID", {})

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