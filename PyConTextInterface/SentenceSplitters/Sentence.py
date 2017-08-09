class Sentence:
    """This class represents the standard Sentence object that should be produced by all sentence splitters. It is
    consumed by PyConText in order to standardize the interface between PyConText and any sentence splitters that may
    be added in the future. All sentence splitters must provide the document span for any text that will be consumed
    by PyConText. This is recorded in the `documentSpan` attribute of the Sentence object."""
    def __init__(self, text, documentSpan, documentName, documentLength):
        self.text = text
        self.documentSpan = documentSpan
        self.documentName = documentName
        self.documentLength = documentLength