"""
This module was created to handle notes with multiple instances of the same sentence. This is only necessary because the PyConText module determines a sentence's location within a note based on a string search. If a sentence appears multiple times in a note then the string search will return all instances of that sentence. We need some way to keep track of which instance we are analyzing. That is the job of this module.
"""

import re


class Sentence:
    def __init__(self, text):
        self.text = text
        self.endOfLastSearch = 0


class SentenceRepeatManager:
    def __init__(self):
        self.sentences = []

    def reset(self):
        """
        Erases this instance's memory of the sentences it has seen before.

        :return: None
        """
        self.sentences = []

    def processSentence(self, sentence, note):
        """
        Keeps track of sentences that appear multiple times in a document so that successive calls to `
        processSentence return the span of the next instance of the sentence instead of returning the
        same span multiple  times. For each new note the `reset` method must be called or a new instance
        of `SentenceRepeatManger` must be created.

        :param sentence: [string] A string to search for in `note`.
        :param note: [string] The note body which contains `sentence`.
        :return: [tuple] A 2-tuple of integers, (spanStart, spanEnd).
        """
        foundSentence = None

        # if the sentence has been seen before it will be in self.sentences, search for it there first
        for storedSentence in self.sentences:
            if storedSentence.text == sentence:
                foundSentence = storedSentence
                break

        # if the sentence is new, add it to the list of sentences.
        if not foundSentence:
            foundSentence = Sentence(sentence)
            self.sentences.append(foundSentence)

        # find the start and end of the appropriate match and return it as a string-ified tuple
        regex = re.compile(re.escape(sentence))
        # only search from where we left off last time we saw the sentence
        match = regex.search(note, foundSentence.endOfLastSearch)
        if match:
            foundSentence.endOfLastSearch = match.end()
            return (match.start(), match.end())
        else:
            raise RuntimeError ("Sentence Repeat Manger: Could not find sentence in note.\n\nSentence:********************************************** \n%s\n\nNote:******************************************************\n %s"
                                % (sentence, note))

