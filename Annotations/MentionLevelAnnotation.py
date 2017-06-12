"""This class represents a single mention-level annotation. """
from time import gmtime, strftime


class MentionLevelAnnotation:
    def __init__(self, sourceDocId, text, start, end, annotator, annotationId, annotationClass = None, creationDate = None):
        self.text = text
        self.start = start
        self.end = end
        self.annotationClass = annotationClass
        self.annotator = annotator
        self.annotationId = annotationId
        if creationDate:
            self.creationDate = creationDate
        else:
            self.creationDate = strftime("%a %b %d %H:%M:%S GMT %Y", gmtime())


    @classmethod
    def overlap(cls, firstAnnotation, secondAnnotation):

        # Overlapping case 1
        if firstAnnotation.start > secondAnnotation.start and firstAnnotation.start < secondAnnotation.end:
            return True

        # Overlapping case 2
        if firstAnnotation.end < secondAnnotation.end and firstAnnotation.end > secondAnnotation.start:
            return True

        # Subset case 1
        if firstAnnotation.start < secondAnnotation.start and firstAnnotation.end > secondAnnotation.end:
            return True

        # Subset case 2
        if firstAnnotation.start > secondAnnotation.start and firstAnnotation.end < secondAnnotation.end:
            return True

        # No overlap
        return False
