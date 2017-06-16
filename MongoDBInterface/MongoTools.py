from pymongo import MongoClient
import pymongo.errors
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document


def constructMongoDocument(annotationDocument):
    annotatorName = ""
    annotations = []
    for index, annotation in enumerate(annotationDocument.annotations.values()):
        if index == 0:
            annotatorName = annotation.annotator
        newAnnotation = {}
        newAnnotation["text"] = annotation.text
        newAnnotation["span_start"] = annotation.start
        newAnnotation["span_end"] = annotation.end
        newAnnotation["annotation_id"] = annotation.annotationId
        newAnnotation["class"] = annotation.annotationClass
        newAnnotation["attributes"] = {}
        for key, value in annotation.attributes.iteritems():
            newAnnotation["attributes"][key] = value
        annotations.append(newAnnotation)

    mongoDocument = {
            "document_name" : annotationDocument.documentName,
            "annotation_group" : annotationDocument.annotationGroup,
            "annotator_name" : annotatorName,
            "annotations" : annotations
        }

    return mongoDocument

def constructAnnotationDocument(mongoDocument):

    annotationGroup = mongoDocument["annotation_group"]
    documentName = mongoDocument["document_name"]
    annotator = mongoDocument["annotator_name"]
    annotations = {}
    for annotation in mongoDocument["annotations"]:
        text = annotation["text"]
        start = annotation["span_start"]
        end = annotation["span_end"]
        annotationId = annotation["annotation_id"]
        attributes = {}
        for key, value in annotation["attributes"].iteritems():
            attributes[key] = value
        annotationClass = annotation["class"]

        annotations[annotationId] = MentionLevelAnnotation(text, start, end, annotator, annotationId, attributes, annotationClass)

    return Document(documentName, annotationGroup, annotations)


class MongoTools:

    @classmethod
    def InsertSingleDocument(cls, document, annotationRound, database='Annotations', host='localhost', port='27017'):

        client = MongoClient('mongodb://%s:%s/' % (host, port))
        collection = client.NLP.Annotations

        mongoDocument = constructMongoDocument(document, annotationRound)
        result = collection.insert_one(mongoDocument)

        client.close()
        return result

    @classmethod
    def InsertMultipleDocuments(cls, documents, annotationRound):

        mongoDocuments = []

        for document in documents:
            mongoDocuments.append(constructMongoDocument(document))

        client = MongoClient()
        collection = client.NLP.Annotations
        result = None
        try:
            result = collection.insert_many(mongoDocuments)
        except pymongo.errors.BulkWriteError as bulkError:
            print "A bulk write exception occured:"
            print bulkError.details
            exit(1)

        client.close()

        return result

    @classmethod
    def findOneDocument(cls, queryDocument):
        client = MongoClient()
        collection = client.NLP.Annotations

        mongoDoc = collection.find_one(queryDocument)
        client.close()
        return constructAnnotationDocument(mongoDoc)

    @classmethod
    def findMultipleDocuments(cls, queryDocument):
        client = MongoClient()
        collection = client.NLP.Annotations

        mongoDocs = collection.find(queryDocument)
        annotationDocs = []

        for mongoDoc in mongoDocs:
            annotationDocs.append(constructAnnotationDocument(mongoDoc))

        client.close()
        return annotationDocs
