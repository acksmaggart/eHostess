MongoDBInterface
****************

The MongoDB Interface allows the user to read and write annotation documents to a MongoDB instance. One MongoDB document corresponds to a single eHostess.Annotations.Document.Document instance and contains multiple individual annotations. An example document can be found at eHostess/MongoDBInterface/ExampleDocument.json. The contents of this file are copied below for convenience:

    .. literalinclude:: ../MongoDbInterface/ExampleDocument.json


==========
MongoTools
==========

.. automodule:: eHostess.MongoDBInterface.MongoTools

.. autofunction:: InsertSingleDocument
.. autofunction:: InsertMultipleDocuments
.. autofunction:: FindOneDocument
.. autofunction:: FindMultipleDocuments
