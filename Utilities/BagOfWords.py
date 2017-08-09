"""The effectiveness of pyConText is heavily dependant on the choice of target and modifier terms. While many target and modifier terms are intuitive there may be useful terms that the user hasn't thought of, whose inclusion in the target or modifier file would improve the output of pyConText. One way to identify these terms is using the "bag of words" approach. This approach requires a text corpus whose documents have already been classified into two or more target categories using some reliable standard. Next the documents in each of the classes is tokenized and the frequency of each token is recorded in a matrix whose rows represent a document and whose columns represent the frequencies of a particular token in each document. It is important to preserve a structure that can be used to map column indices to tokens so that the columns of interest can be mapped back to strings at the end of the process. After constructing this matrix typically univariate analysis is performed to compare the distribution of a column in one document-classification group to the distribution of the corresponding columns in other classification groups. By comparing distributions the user can detect which tokens are more prevelant in classfication groups of interest. This method may even be used as a document classification strategy on its own.

This module contains functions for converting text into Numpy sparse matrices suitable for analysis.
"""

def createBagOfWords(documentDictionaryList):
    """
    This function takes a list of dictionary objects containing the text corpus and returns a
    :param documentDictionary:
    :return:
    """