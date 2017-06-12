
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
    print "Passed"
else:
    print '*****************Test Failed***************************'
# duplicateProcessor.reportDuplicates()


#### Test path cleaner, turns path strings into glob-able directory strings. ####
from NotePreprocessing.Preprocessor import cleanDirectoryList as cleaner

print 'Testing Preprocessor.cleanDirectoryList()'
dirs = ['/Some/path/to/stuff', '/Some/path/to/stuff/', '/Some/path/to/stuff/*']
cleanDirs = cleaner(dirs)
fail = False
for dirName in cleanDirs:
    if dirName != '/Some/path/to/stuff/*':
        print '*****************Test Failed***************************'
        fail = True
if not fail:
    print 'Passed\n'