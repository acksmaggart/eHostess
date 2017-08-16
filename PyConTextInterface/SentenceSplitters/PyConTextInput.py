"""As its name suggests this module is meant to serve as the common interface between sentence splitters and PyConText. Specifically, all sentence splitter implementations should return a single instance of this class when its 'splitSentences' method is called, since the PyConText module consumes only single-instances of this class to perform annotation. It is effectively a dictionary, keyed by document name, whose values are lists of Sentence objects. All sentence splitter implementations must ensure that there is a document key for each note processed by the splitter regardless of whether or not any sentences were produced from that note. For notes which do not produce any sentences, e.g. notes processed by the TargetSpanSplitter that do not contain any target terms, the splitter should call PyConTextInput.addDocumentPlaceholder() rather than addSentence(). If the number of keys output by the sentence splitter does not match number of input documents then calls to eHostess.Analysis.DocumentComparison.CompareDocumentBatches will likely fail. In other words, just as a Knowtator.xml file is produced for every human-annotated note in eHost regardless of whether or not any text was annotated in that note, every sentence splitter implementation should output a key for every note regardless of whether it actually produced a sentence from that note."""

class Sentence:
    """This class is a helper class for PyConTextInput. It represents a sentence that is produced by a sentence splitter.
    All sentence splitters must provide the document span for any text that will be consumed by PyConText. This is recorded in the `documentSpan` attribute of the Sentence object."""
    def __init__(self, text, documentSpan, documentName, documentLength, targetRegex=None):
        """
        :param text: [String] The text of the sentence.
        :param documentSpan: [tuple (int, int)] The location of the sentence within its note.
        :param documentName:  [string] The name of the note as parsed by Document.ParseDocumentNameFromPath
        :param documentLength: [int] The number of characters in the document.
        :param targetRegex: [string] If the target span splitter is used to split the sentences it will populate this
        field to specify which target term was intended to be annotated in the case of a span that contains multiple
        target terms.
        """
        self.text = text
        self.documentSpan = documentSpan
        self.documentName = documentName
        self.documentLength = documentLength
        self.targetRegex = targetRegex

    @classmethod
    def sameContents(cls, sentence1, sentence2):
        if sentence1.text != sentence2.text:
            return False
        if sentence1.documentSpan != sentence2.documentSpan:
            return False
        if sentence1.documentName != sentence2.documentName:
            return False
        if sentence1.documentLength != sentence2.documentLength:
            return False
        return True

class DocumentPlaceholder:
    """This class represents a scenario in which a sentence splitter processes a note but does not produce any sentences for that note. Sentence splitters should call PyConTextInput.addDocumentPlaceholder any time they encounter a note for which they would not normally produce any sentences. For example, if the TargetSpanSplitter encounters a note in which there are no target terms no sentences will be produced and the splitter should call addDocumentPlaceholder passing the name of that note as an argument to indicate that the note was processed but that no sentences were produced.
    This class does not possess any attributes or methods because it is intended to be used only as an argument to type() in the PyConText module."""


class PyConTextInput(dict):
    def __init__(self, numDocs=None, *args):
        """
        If numDocs is not None then the user may use the method 'containsExpectedNumberOfDocKeys()' to ensure that  the number of document keys contained in their instance of PyConTextInput is the expected number.
        :param numDocs: [int] The number of documents to be processed by the sentence splitter, also the number of keys that should be present in the dictionary when the PyConTextInput instance is done being created.
        :param args:
        """
        super(PyConTextInput, self).__init__(args)
        self.numDocs = numDocs

    def addSentence(self, sentenceText, documentSpan, documentName, documentLength, targetRegex=None):
        newSentence = Sentence(sentenceText, documentSpan, documentName, documentLength, targetRegex)

        if documentName in self:
            if isinstance(self[documentName], DocumentPlaceholder):
                raise RuntimeError("addSentence has been called using a note for which a DocumentPlaceholder has already been created. DocumentPlaceholders should only be created for notes that do not produce any sentences.")
            else:
                self[documentName].append(newSentence)
        else:
            self.__setitem__(documentName, [])
            self[documentName].append(newSentence)

    def addDocumentPlaceholder(self, documentName):
        if documentName in self:
            if isinstance(self[documentName], list):
                raise RuntimeError("Document placeholders should only be created for documents that have not produced any sentences. There is/are %i sentence(s) already stored for note %s." % (len(self[documentName]), documentName))
            if isinstance(self[documentName], DocumentPlaceholder):
                raise RuntimeError("A document placeholder has already been created for note %s." % documentName)
        else:
            self.__setitem__(documentName, DocumentPlaceholder())

    def containsExpectedNumberOfDocKeys(self):
        if len(self.keys()) == self.numDocs:
            return True
        else:
            return False
