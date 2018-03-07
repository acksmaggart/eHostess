"""
This module contains several functions that allow the user to read and write annotation documents using a MongoDB backing store. I recommend creating a unique index in whichever collection will hold the annotation documents to ensure that no two documents have the same combination of document name, annotator name, and annotation round.
"""

from pymongo import MongoClient
import pymongo.errors
from ..Annotations.MentionLevelAnnotation import MentionLevelAnnotation
from ..Annotations.Document import Document


def constructMongoDocument(annotationDocument):
    annotatorName = ""
    annotations = []
    for index, annotation in enumerate(annotationDocument.annotations):
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
            "annotations" : annotations,
            "num_characters" : annotationDocument.numberOfCharacters
        }

    return mongoDocument

def constructAnnotationDocument(mongoDocument):

    annotationGroup = mongoDocument["annotation_group"]
    documentName = mongoDocument["document_name"]
    annotator = mongoDocument["annotator_name"]
    numChars = mongoDocument["num_characters"]
    annotations = []
    for annotation in mongoDocument["annotations"]:
        text = annotation["text"]
        start = annotation["span_start"]
        end = annotation["span_end"]
        annotationId = annotation["annotation_id"]
        attributes = {}
        for key, value in annotation["attributes"].iteritems():
            attributes[key] = value
        annotationClass = annotation["class"]

        annotations.append(MentionLevelAnnotation(text, start, end, annotator, annotationId, attributes, annotationClass))

    return Document(documentName, annotationGroup, annotations, numChars)


def InsertSingleDocument(document, annotationRound, database='NLP', collection="Annotations", host='localhost', port='27017'):
    """
    Writes a single Document object to the MongoDB store using the specified database parameters.

    :param document: [Object] A Document object to store in the MongoDB database.
    :param annotationRound: [string] The name of the current annotation round.
    :param database: [string] The name of the MongoDB database instance that holds "collection". Defaults to NLP.
    :param collection: [string] The name of the collection that stores the document instances. Defaults to "Annotations".
    :param host: [string] The host IP address, defaults to localhost.
    :param port: [string] The port on which the MongoDB server is listening. Defaults to 27017.
    :return: [object] An instance of pymongo.results.InsertOneResult, the default object returned by MongoDB following an "insert_one" operation.
    """
    client = MongoClient('mongodb://%s:%s/' % (host, port))
    collection = client[database][collection]

    mongoDocument = constructMongoDocument(document)
    result = collection.insert_one(mongoDocument)

    client.close()
    return result


def InsertMultipleDocuments(documents, annotationRound, database='NLP', collection="Annotations", host='localhost', port='27017'):
    """
    Writes multiple Document objects to the MongoDB store using the specified database parameters.

    :param documents: [list of Objects] A list of Document objects to store in the MongoDB database.
    :param annotationRound: [string] The name of the current annotation round.
    :param database: [string] The name of the MongoDB database instance that holds "collection". Defaults to NLP.
    :param collection: [string] The name of the collection that stores the document instances. Defaults to "Annotations".
    :param host: [string] The host IP address, defaults to localhost.
    :param port: [string] The port on which the MongoDB server is listening. Defaults to 27017.
    :return: [object] An instance of pymongo.results.InsertManyResult, the default object returned by MongoDB following an "insert_many" operation.
    """

    mongoDocuments = []

    for document in documents:
        mongoDocuments.append(constructMongoDocument(document))

    client = MongoClient('mongodb://%s:%s/' % (host, port))
    collection = client[database][collection]
    result = None
    try:
        result = collection.insert_many(mongoDocuments)
    except pymongo.errors.BulkWriteError as bulkError:
        print "A bulk write exception occured:"
        print bulkError.details
        exit(1)

    client.close()

    return result

def FindOneDocument(queryDocument, database='NLP', collection="Annotations", host='localhost', port='27017'):
    """
    This method returns the first document in the backing store that matches the criteria specified in queryDocument.

    :param queryDocument: [dict] A pymongo document used to query the MongoDB instance.
    :param database: [string] The name of the MongoDB database instance that holds "collection". Defaults to NLP.
    :param collection: [string] The name of the collection that stores the document instances. Defaults to "Annotations".
    :param host: [string] The host IP address, defaults to localhost.
    :param port: [string] The port on which the MongoDB server is listening. Defaults to 27017.
    :return: [object | None] A single Document object if the query matches any documents, otherwise None.
    """

    client = MongoClient('mongodb://%s:%s/' % (host, port))
    collection = client[database][collection]

    mongoDoc = collection.find_one(queryDocument)
    client.close()

    return constructAnnotationDocument(mongoDoc)

def FindMultipleDocuments(queryDocument, database='NLP', collection="Annotations", host='localhost', port='27017'):
    """
    Executes a "find" operation on the MongoDB instances and returns a list of all the annotation documents that match the criteria specified in queryDocument.

    :param queryDocument: [dict] A pymongo document used to query the MongoDB instance.
    :param database: [string] The name of the MongoDB database instance that holds "collection". Defaults to NLP.
    :param collection: [string] The name of the collection that stores the document instances. Defaults to "Annotations".
    :param host: [string] The host IP address, defaults to localhost.
    :param port: [string] The port on which the MongoDB server is listening. Defaults to 27017.
    :return: [list of objects | None] A list of Document objects, or None if queryDocument does not match any documents in the backing store.
    """

    client = MongoClient('mongodb://%s:%s/' % (host, port))
    collection = client[database][collection]

    mongoDocs = collection.find(queryDocument)
    annotationDocs = []

    for mongoDoc in mongoDocs:
        annotationDocs.append(constructAnnotationDocument(mongoDoc))

    client.close()
    return annotationDocs
