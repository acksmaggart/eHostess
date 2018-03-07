from ..Utilities.utilities import cleanDirectoryList
import glob
import re
import os

class Note:
    def __init__(self, fileName, body):
        self.fileName = fileName
        self.body = body
        self.regex = re.compile(re.escape(body))

class ExactDuplicateManager:
    def __init__(self):
        self.exactDuplicatesToKeep = {}

    def processPair(self, name1, name2):
        """Returns the name to delete."""
        if name1 in self.exactDuplicatesToKeep:
            return name2
        elif name2 in self.exactDuplicatesToKeep:
            return name1
        else:
            self.exactDuplicatesToKeep[name1] = True
            return name2


class DuplicateProcessor:
    """This class detects notes whose content is a duplication or subset of another note."""

    def __init__(self, corpusDirectoryList):
        self.corpusDirectoryList = cleanDirectoryList(corpusDirectoryList)
        self.notesProcessed = False
        self.notes = []
        self.subsetsToRemove = []
        self.exactDuplicatesToRemove = []
        self.exactDuplicatesToKeep = {}

    def findDuplicates(self):
        print("Finding duplicates...")
        # Reset duplicatesToRemove list and duplicatePairs list in case the user is using the same instance
        # to check multiple batches.
        self.subsetsToRemove = []
        self.duplicatePairs = []
        self.exactDuplicatesToKeep = {}

        #Find duplicates:
        for dir in self.corpusDirectoryList:

            files = glob.glob(dir)

            for file in files:
                fileHandle = open(file, 'r')
                noteBody = fileHandle.read()
                newNote = Note(file, re.sub('\r\n', '\n', noteBody))
                self.notes.append(newNote)
                fileHandle.close()

        totalComparisons = float(len(self.notes))**2
        completeComparisons = 0

        for outerNote in self.notes:
            regex = re.compile(re.escape(outerNote.body))
            for innerNote in self.notes:
                completeComparisons += 1.
                if completeComparisons % 100000. == 0:
                    print('Completed %d of %d comparisons. %d%%' % (completeComparisons, totalComparisons, completeComparisons/totalComparisons))
                if outerNote is innerNote:
                    continue
                # Outer note is a subset of the inner note, or they are duplicates.
                match = regex.search(innerNote.body)
                if match:

                    # notes are exact duplicates:
                    if len(outerNote.body) == len(innerNote.body):
                        if outerNote.fileName in self.exactDuplicatesToKeep:
                            self.exactDuplicatesToRemove.append(innerNote)
                        elif innerNote.fileName in self.exactDuplicatesToKeep:
                            self.exactDuplicatesToRemove.append(outerNote)
                        else:
                            self.exactDuplicatesToKeep[outerNote.fileName] = True
                            self.exactDuplicatesToRemove.append(innerNote)
                    # Outer note is a subset of inner note.
                    else:
                        self.subsetsToRemove.append(outerNote)

        # If there are three identical notes the above method will add two of the notes twice. So remove duplicates in
        # the list to avoid unlinking a file twice.
        self.subsetsToRemove = self._removeDuplicatesFromList(self.subsetsToRemove)
        self.exactDuplicatesToRemove = self._removeDuplicatesFromList(self.exactDuplicatesToRemove)

        self.notesProcessed = True
        print("Done finding duplicates.\n")

    def findNonDuplicates(self):
        print("Finding non-duplicates...")
        # Reset duplicatesToRemove list and duplicatePairs list in case the user is using the same instance
        # to check multiple batches.

        nonDuplicates = []

        print("Creating Notes...")
        count = 0
        for dir in self.corpusDirectoryList:

            files = glob.glob(dir)

            for file in files:
                fileHandle = open(file, 'r')
                noteBody = fileHandle.read()
                newNote = Note(file, re.sub('\r\n', '\n', noteBody))
                self.notes.append(newNote)
                fileHandle.close()
                count += 1
                print("%d of %d" % (count, len(files)))


        totalComparisons = float(len(self.notes))**2
        completeComparisons = 0

        nonDupCount = 0
        for i in range(len(self.notes)):
            outerNote = self.notes[i]
            subset = False
            for k in range(i+1, len(self.notes)):
                innerNote = self.notes[k]
                completeComparisons += 1.
                if completeComparisons % 100000. == 0:
                    print('Completed %d of %d comparisons. %d%%' % (completeComparisons, totalComparisons, completeComparisons/totalComparisons))
                if outerNote is innerNote:
                    continue
                # Outer note is a subset of the inner note, or they are duplicates.
                matchOuterSubset = outerNote.regex.search(innerNote.body)
                matchInnerSubset = innerNote.regex.search(outerNote.body)

                if matchOuterSubset or matchInnerSubset:
                    subset = True
                    break
            if not subset:
                nonDupCount += 1
                print("%s  %d" % (outerNote.fileName, nonDupCount))
                nonDuplicates.append(outerNote)

        # If there are three identical notes the above method will add two of the notes twice. So remove duplicates in
        # the list to avoid unlinking a file twice.
        self.subsetsToRemove = self._removeDuplicatesFromList(self.subsetsToRemove)
        self.exactDuplicatesToRemove = self._removeDuplicatesFromList(self.exactDuplicatesToRemove)

        self.notesProcessed = True
        print("Done finding duplicates.\n")

    def reportDuplicates(self, verbose=True):
        if not self.notesProcessed:
            raise ValueError("Notes have not been processed yet. Call processNotes() first.")

        if len(self.exactDuplicatesToRemove) == 0 and len(self.subsetsToRemove) == 0:
            print "No duplicates found."
            return

        print("%d notes were found that were subsets of other notes." % len(self.subsetsToRemove))
        if verbose and len(self.subsetsToRemove) != 0:
            print("Notes that were subsets:")
            for note in self.subsetsToRemove:
                print(note.fileName)

        print('\n\n')
        print("%d notes were found that were exact duplicates of other notes." % len(self.exactDuplicatesToRemove))
        if verbose and len(self.exactDuplicatesToRemove) != 0:
            print("Notes that were exact duplicates:")
            for note in self.exactDuplicatesToRemove:
                print(note.fileName)

        print('\n\n')
        print("After taking the union of the duplicate notes and subset notes there are %d notes to be deleted."
              % len (self._getUnionOfDuplicatesAndSubsets()))
        if verbose:
            print("Notes to be deleted:")
            for note in self._getUnionOfDuplicatesAndSubsets():
                print(note.fileName)

        print("\n")

    def removeDuplicates(self):
        if not self.notesProcessed:
            raise ValueError("Notes have not been processed yet. Call processNotes() first.")

        print("Removing duplicates...")
        for note in self._getUnionOfDuplicatesAndSubsets():
            os.remove(note.fileName)
            print("Done removing duplicates.\n")

    def _removeDuplicatesFromList(self, rawList):
        rawSorted = sorted(rawList, key=lambda note: note.fileName)
        uniqueNotes = []
        previousName = None
        for note in rawSorted:
            if previousName == None:
                previousName = note.fileName
                uniqueNotes.append(note)
                continue
            if note.fileName != previousName:
                previousName = note.fileName
                uniqueNotes.append(note)

        return uniqueNotes

    def _getUnionOfDuplicatesAndSubsets(self):
        combinationList = self.exactDuplicatesToRemove + self.subsetsToRemove
        return self._removeDuplicatesFromList(combinationList)


class TextAlteration():
    def __init__(self, corpusDirectoryList):
        self.corpusDirectoryList = cleanDirectoryList(corpusDirectoryList)
        self.fileNames = self.createFileNameList()

    def appendText(self, text, numNewLines = 0):
        for fileName in self.fileNames:
            with open(fileName, 'a') as currentFile:
                for i in range(numNewLines):
                    currentFile.write('\n')
                currentFile.write(text)

    def createFileNameList(self):
        fileNames = []
        for dir in self.corpusDirectoryList:
            fileNames.extend(glob.glob(dir))
        return fileNames






