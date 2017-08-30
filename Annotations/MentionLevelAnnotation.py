from time import gmtime, strftime


class MentionLevelAnnotation:
    """This class represents a single mention-level annotation. For example, a single highlight in eHost or a single node in PyConText. It currently only has one method, a class method for determining if two mention-level annotations overlap with one another."""
    def __init__(self, text, start, end, annotator, annotationId, attributes, annotationClass = None, creationDate = None, dynamicProperties={}):
        """
        :param text: [string] The text includes the target term, e.g. the highlighted text in eHost.
        :param start: [int] The position in the document where annotation starts.
        :param end: [int] The position in the document where annotation ends.
        :param annotator: [string] The name of the annotator, or annotation method used to produce the annotation.
        :param annotationId: [string] An ID belonging to the annotation that should be unique to its document. This uniqueness is not currently enforced anywhere. This attribute was included mainly because it is present in eHost output files.
        :param attributes: [dict] A dictionary of attributes, with attribute names as the keys and attribute values as the values. Annotations in eHost have 'attributes', 'classes', and 'relationships'. This package currently only supports annotation attributes and classes. Annotations may only have a single 'class' but may have many 'attributes'. The 'attributes' property of MentionLevelAnnotation objects in this package represents the eHost attributes. However, it is of course possible to produce annotations using other methods that possess attributes, e.g. pyConText.
        :param annotationClass: [string] The class to which the annotation has been assigned. This attribute represents the eHost class of an annotation, however, like the 'attributes' attribute the 'annotationClass' attribute is meant to be more general, allowing the user to populate it with a value produced using an arbitrary annotation method.
        :param creationDate: [string] A string representing the time that this annotation was created. If None (default) the annotation is labeled with the time that is was created in GMT.
        :param dynamicProperties: [dict] This property is meant to store miscellaneous information assiciated with the annotation that may be useful to preserve, but does not fit into the semantics of eHost's annotation objects or analysis. For example, the PyConText module stores the PyConText target term in this dictionary using the key 'target' to help human users review the output of the algorithm during optimization..
        """
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
        if not isinstance(dynamicProperties, dict):
            raise ValueError("dynamicProperties must be a dictionary or a subclass of dict. Got <%s>." % type(dynamicProperties))
        self.dynamicProperties = dynamicProperties


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


