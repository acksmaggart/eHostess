"""
This module was created in order to help record the document span of an annotation identified by pyConText.
The approach chosen to record the document span was to split the document into sentences and then search for
each sentence in the document to find its original span. However, the sentence splitter alters the white space
of sentences containing newline characters and multiple contiguous whitespace characters. Therefore it is
necessary to reconstruct the sentences after they have been split, restoring the original whitespace
characters, before performing the string match to find the document span. Without reconstructing the sentence any
target that is identified following altered whitespace characters will have an incorrect span when its document
span is calculated.
This module assumes that sentences are passed to `reconstructSentence()` in the same order that they appear in
the note body and that the only alteration that has occured is the addition or deletion of whitespace
characters.
"""

import re


class SentenceReconstructor:
    def __init__(self, noteBody=""):
        self.noteBody = noteBody
        self.noteCursor = 0

    def startNewNote(self, newNoteBody):
        self.noteBody = newNoteBody
        self.noteCursor = 0

    def reconstructSentence(self, alteredSentence):
        """
        This method first strips the input sentence of all whitespace characters. It then scans through the
        sentence and through the note (from the last place it left off) checking to see if they match. If there
        is a mismatch and the note cursor points to a whitespace character it is inserted into the sentence.
        If there is a mismatch and the note cursor does not point to a whitespace character an exception
        is raised.
        :param alteredSentence: [string] The sentence from the note body that has been altered by the sentence splitter.
        :return: [string] The reconstructed sentence.
        """
        sentenceWithoutWhitespace = re.sub(r"\n|\r| |\t","",alteredSentence)
        sentenceCursor = 0
        reconstructedSentence = ""
        while sentenceCursor < len(sentenceWithoutWhitespace):
            nextNoteCharacter = self.noteBody[self.noteCursor]
            nextSentenceCharacter = sentenceWithoutWhitespace[sentenceCursor]
            if nextNoteCharacter == nextSentenceCharacter:
                reconstructedSentence += nextNoteCharacter
                self.noteCursor += 1
                sentenceCursor += 1
                continue

            if nextNoteCharacter in '\n\r \t':
                reconstructedSentence += self.noteBody[self.noteCursor]
                self.noteCursor += 1
                continue

            # If we reach this point there is a mismatch and something is wrong
            raise RuntimeError("There is a non-whitespace mismatch. Note Snippet: %s\nSentence Snippet: %s\n" %
                               (self.noteBody[self.noteCursor: self.noteCursor + 10],
                                sentenceWithoutWhitespace[sentenceCursor: sentenceCursor + 10]))

        return reconstructedSentence