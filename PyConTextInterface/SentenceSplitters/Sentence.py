class Sentence:
    """This class represents the standard Sentence object that should be produced by all sentence splitters. It is
    consumed by PyConText in order to standardize the interface between PyConText and any sentence splitters that may
    be added in the future. All sentence splitters must provide the document span for any text that will be consumed
    by PyConText. This is recorded in the `documentSpan` attribute of the Sentence object."""
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