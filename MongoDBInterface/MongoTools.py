from pymongo import MongoClient

class MongoTools:


    @classmethod
    def WriteDocument(cls, document, annotationRound, database='Annotations', host='localhost', port='27017'):

        client = MongoClient('mongodb://%s:%s/' % (host, port))
        collection = client.NLP.Annotations

        annotatorName = ""
        annotations = []
        for index, annotation in enumerate(document.annotations.values):
            if index == 0:
                annotatorName = annotation.annotator
            newAnnotation = {}
            newAnnotation["text"] = annotation.text
            newAnnotation["span_start"] = annotation.start
            newAnnotation["span_end"] = annotation.end
            newAnnotation["annotation_id"] = annotation.annotationId
            newAnnotation["class"] = annotation.annotationClass
            newAnnotation["attributes"] = {}
            for key, value in annotation.attributes:
                newAnnotation["attributes"][key] = value
            annotations.append(newAnnotation)


        collection.insertOne({
            "document_name" : document.documentName,
            "document_id" : document.documentId,
            "annotation_round" : annotationRound,
            "annotator_name" : annotatorName,
            "annotations" : annotations
        })
