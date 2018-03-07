"""Often in medical text sentence structure is irregular and sentence boundaries are poorly defined. As a result
sentence splitters developed for use with conventional english text often produce very large sentences when
used to split a medical note. Occasionally, these large sentences will encompass multiple thoughts and
modifier words at the beginning of the text chunk will be incorrectly applied to targets at the end of the chunk that
appear as part of a separate thought. For example, consider the following text chunk that may be output from a
conventional sentence splitter:
    "...Medical History: No history of stroke

    HPI: Patient presents with GI bleed..."

In this case 'No' from 'No history of stroke' will be incorrectly applied to 'GI Bleed' because there was no period at
the end of the "Medical History" section.

This module is designed to split the note by first identifying the location of target terms and returning a
configurable span of text on either side of the target terms. This guarantees that sentences returned by the sentence
splitter do not exceed a certain length. However, it may mean that target terms are included in multiple sentences. For
example consider the following section of text:

"...some associated nausea and vomiting.  No
blood, no coffee-grounds, no fevers, chills, or anorexia.  He
said that this..."

There are two target terms in this sentence: "blood" and "coffee-grounds". And as a result the span-based sentence
splitter will return two sentences, one for each target term. Unless the module is configured to take only a few
characters on either side of the target term both terms will be included in both sentences. As a result, both terms will
be annotated twice by pyConText. In consideration of this problem the PyConText module always checks to make sure that
no two nodes point to the same target before creating the annotation document regardless of the sentence splitter used.

IMPORTANT: This module uses the same ItemData targets that PyConText uses to perform its annotations.
If the user wishes to match target terms that include multiple words they should ensure that they account for
cases in which the target phrase spans multiple lines. e.g. "bright red blood\nper rectum". If the target regular
expression is the literal phrase, "bright red blood per rectum" then the example phrase above will not match due to the
presence of the newline character. A simply solution to this problem is to use the regex pattern '\s+' in place of all
spaces (" ") to match any irregular whitespace. e.g. "bright\s+red\s+blood\s+per\s+rectum" will match regardless of line
breaks or other unexpected whitespace.
The use of '\s+' is not necessary when running PyConText with the built-in sentence
splitter because the built-in splitter effectively replaces all whitespaces in the document with single spaces before
splitting the sentences. This approach is not desirable for this module, however, because the span-based sentence splitter
only returns a small portion of the total note; those portions containing a target term or phrase. As a result, if the
whitespace in the returned section has been altered it would be impossible to reliably determine the target's document
span due to the presence of repeat sentences. Bottom-line: It is highly recommended when using this span-based splitter
to use '\s+' in place of all space characters in target regular expressions to avoid missing targets that include
unexpected whitespace.

Issues:
"History of GI Bleed, with other things." Regex stops at the comma. Fix: Add [,\-:]? to end of all target regex's, or custom punctuation set.
"""

import re
from PyConTextInput import PyConTextInput
from eHostess.Annotations.Document import Document
import eHostess.Utilities.utilities as utilities
import glob
import sys
import multiprocessing

def _splitSentencesSingleDocumentInternal(documentPath, targets, numLeadingWords, numTrailingWords, spanTargetPunctuation):
    """This function takes a document path and splits it up according to the other paramaters, returning a tuple of the form (text, docSpanTuple, docName, docLength, None) to be fed to PyConTextInput. Or (None, <docName>) if no target terms were matched in the input doc."""

    with open(documentPath, 'rU') as inFile:
        documentText = inFile.read()

    documentName = Document.ParseDocumentNameFromPath(documentPath)

    defaultPunctuationToIgnore = "[,:-]?"
    punctuationToIgnore = ""
    if spanTargetPunctuation == None:
        punctuationToIgnore = defaultPunctuationToIgnore
    if spanTargetPunctuation != False and spanTargetPunctuation != None:
        punctuationToIgnore = spanTargetPunctuation


    regexStrings = [(r"(?:[^\.\s]+\s+){0,%i}(%s)%s(?:\s+[^\.\s]+){0,%i}" %
                                    (numLeadingWords, item.getRE(), punctuationToIgnore, numTrailingWords), item.getRE()) for item in targets]

    matches = [(match, targetRegex) for regexString, targetRegex in regexStrings for match in re.finditer(regexString, documentText, flags=re.IGNORECASE)]

    if len(matches) == 0:
        return (None, documentName)
    else:
        return [(match[0].group(), (match[0].start(), match[0].end()), documentName, len(documentText), match[1]) for match in matches]

def splitSentencesSingleDocument(documentPath, targets, numLeadingWords, numTrailingWords, spanTargetPunctuation=None):
    """
    This function splits the input documentText into sections, taking a span around the document as specified by
    numLeadingWords and numTrailingWords. The span is taken by finding all matches of the regular expression
    (?:[^\.\s]+\s+){0,<numLeadingWords>}(<targetRegularExpression>)<punctuationToIgnore>(?:\s+[^\.\s]+){0,<numTrailingWords>}
    See the explanation of the 'spanTargetPunctuation' argument for more info about <punctuationToIgnore>.

    :param documentPath: (string) The path to the document to split into target-span regions.
    :param targets: (pyConText.itemData.itemData) The pyConText itemData instance that contains the target ContextItems.
    :param numLeadingWords: (int) The number of words before the target term to include in the span.
    :param numTrailingWords: (int) The number of words following the target term to include in the span.
    :param spanTargetPunctuation: (optional) If False, the regex will not grab any words after the target if the target is
    followed immediately by punctuation. e.g. "History of GI Bleed, and some other things you might want" will only
    return up through "Bleed" since the comma does not match a word boundary. By default this function will continue past
    the punctuation characters "," ":" and "-" but not ".". The user may specify different non-word characters to ignore
    by passing a string as an argument. This string is inserted without modification at the
     <punctuationToIgnore> position in the regular expression used to find the spans. The default string is "[,:-]?"
     See function doc string for more info about the regular expression used to find the spans.
    :return:(list) A list of SpanBasedSentence objects containing information about the spans identified in the docuemnt.
    See `SpanBasedSentence` for more info.
    """

    pyConTextInput = PyConTextInput()

    sentenceTuples = _splitSentencesSingleDocumentInternal(documentPath, targets, numLeadingWords, numTrailingWords, spanTargetPunctuation)

    if sentenceTuples[0][0] == None:
        pyConTextInput.addDocumentPlaceholder(sentenceTuples[0][1])
        return pyConTextInput
    else:
        for sentenceTuple in sentenceTuples:
            pyConTextInput.addSentence(*sentenceTuple)
        return pyConTextInput


def splitSentencesMultipleDocuments(directoryList, targets, numLeadingWords, numTrailingWords,
                                 spanTargetPunctuation=None):
    """
    This function splits the input documentText into sections, taking a span around the document as specified by
    numLeadingWords and numTrailingWords. The span is taken by finding all matches of the regular expression
    (?:[^\.\s]+\s+){0,<numLeadingWords>}(<targetRegularExpression>)<punctuationToIgnore>(?:\s+[^\.\s]+){0,<numTrailingWords>}
    See the explanation of the 'spanTargetPunctuation' argument for more info about <punctuationToIgnore>.

    :param documentPath: (string) The path to the document to split into target-span regions.
    :param targets: (pyConText.itemData.itemData) The pyConText itemData instance that contains the target ContextItems.
    :param numLeadingWords: (int) The number of words before the target term to include in the span.
    :param numTrailingWords: (int) The number of words following the target term to include in the span.
    :param spanTargetPunctuation: (optional) If False, the regex will not grab any words after the target if the target is
    followed immediately by punctuation. e.g. "History of GI Bleed, and some other things you might want" will only
    return up through "Bleed" since the comma does not match a word boundary. By default this function will continue past
    the punctuation characters "," ":" and "-" but not ".". The user may specify different non-word characters to ignore
    by passing a string as an argument. This string is inserted without modification at the
     <punctuationToIgnore> position in the regular expression used to find the spans. The default string is "[,:-]?"
     See function doc string for more info about the regular expression used to find the spans.
    :return:(list) A list of SpanBasedSentence objects containing information about the spans identified in the docuemnt.
    See `SpanBasedSentence` for more info.
    """
    if type(directoryList) != list:
        directoryList = [directoryList]

    cleanList = utilities.cleanDirectoryList(directoryList)

    fileList = [filename for directory in cleanList for filename in glob.glob(directory)]

    sentenceTuples = []
    for index, filepath in enumerate(fileList):
        sys.stdout.write("\rSplitting document %i of %i. (%.2f%%)"% (index + 1, len(fileList) + 1, float(index + 1)/float(len(fileList) + 1) * 100.))
        sys.stdout.flush()
        tupleList = _splitSentencesSingleDocumentInternal(filepath, targets, numLeadingWords, numTrailingWords,spanTargetPunctuation)
        #If the splitter returns (None, <docname>) instead of a list then we should append the tuple rather than
        # extending the list with the contents of the tuple.
        if isinstance(tupleList, list):
            sentenceTuples.extend(tupleList)
        else:
            sentenceTuples.append(tupleList)
    print ""

    pyConTextInput = PyConTextInput(numDocs=len(fileList))
    for sentenceTuple in sentenceTuples:
        if sentenceTuple[0] == None:
            pyConTextInput.addDocumentPlaceholder(sentenceTuple[1])
        else:
            pyConTextInput.addSentence(*sentenceTuple)

    if not pyConTextInput.containsExpectedNumberOfDocKeys():
        raise RuntimeError("The PyConTextInput object produced by PyConTextBuiltinSplitter does not contain the expected number of documents. Expected: %i, Contains: %i" % (pyConTextInput.numDocs, len(pyConTextInput.keys())))

    return pyConTextInput





















