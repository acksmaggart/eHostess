from time import gmtime, strftime


class MentionLevelAnnotation:
    """This class represents a single mention-level annotation. For example, a single highlight in eHost or a single node in PyConText. It currently only has one method, a class method for determining if two mention-level annotations overlap with one another."""
    def __init__(self, text, start, end, annotator, annotationId, attributes, annotationClass = None, creationDate = None):
        self.text = text
        self.start = int(start)
        self.end = int(end)
        self.annotationClass = annotationClass
        self.annotator = annotator
        self.annotationId = annotationId
        if not isinstance(attributes, dict):
            raise ValueError("MentionLevelAnnotation.attributes must be of 'dict' type.")
        else:
            self.attributes = attributes
        if creationDate:
            self.creationDate = creationDate
        else:
            self.creationDate = strftime("%a %b %d %H:%M:%S GMT %Y", gmtime())


    @classmethod
    def overlap(cls, firstAnnotation, secondAnnotation):
        """
        This method determines if the spans of two mention-level annotations overlap. This is a crucial consideration when calculating agreement between two annotators or two annotation methods.

        :param firstAnnotation: [Object] An instance of MentionLevelAnnotation.
        :param secondAnnotation: [Object] A second instance of MentionLevelAnnotation.
        :return: [boolean] True if the two annotations overlap, otherwise False.
        """
        # There should be 11 cases where spans overlap:

        # firstAnnotation and secondAnnotation have the same span
        # firstAnnotation begins in same place as secondAnnotation but ends inside secondAnnotation
        # firstAnnotation begins inside secondAnnotation and they share an end
        if firstAnnotation.start == secondAnnotation.start or firstAnnotation.end == secondAnnotation.end:
            return True

        # firstAnnotation is entirely before secondAnnotation:
        # firstAnnotation end equals secondAnnotation start
        if firstAnnotation.end <= secondAnnotation.start:
            return False

        # firstAnnotation begins before secondAnnotation but ends in middle of secondAnnotation
        # firstAnnotation begins and ends inside secondAnnotation
        if firstAnnotation.end <= secondAnnotation.end and firstAnnotation.end > secondAnnotation.start:
            return True

        # firstAnnotation begins inside secondAnnotation but ends beyond it.
        if firstAnnotation.start >= secondAnnotation.start and firstAnnotation.start < secondAnnotation.end:
            return True

        # firstAnnotation begins at end of secondAnnotation and ends beyond it.
        # firstAnnotation begins and ends beyond secondAnnotation
        if firstAnnotation.start >= secondAnnotation.end:
            return False

        # firstAnnotation entirely encompasses secondAnnotation
        if firstAnnotation.start < secondAnnotation.start and firstAnnotation.end > secondAnnotation.end:
            return True

        # If we get here then there was a case I didn't think of.
        raise NotImplementedError("overlap() was asked to handle a case for which the code does not account. Start1: %i, End1: %i,  Start2: %i, End2: %i" % (firstAnnotation.start, firstAnnotation.end, secondAnnotation.start, secondAnnotation.end))


