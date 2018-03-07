.. eHostess documentation master file, created by
   sphinx-quickstart on Tue Jun 27 12:18:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to eHostess's documentation!
====================================

The eHostess package is designed as a natural language processing tool to work with text. Specifically, eHostess is composed of three main groups of modules:

1. Modules representing annotation data, found in :doc:`eHostess.Annotations <Annotations>`. These modules represent individual annotations as well as annotation documents which are collections of annotations.
2. Modules that create individual annotations and annotation documents by interfacing with outside sources like eHost_ and PyConText_, found in :doc:`eHostess.eHostInterface <eHostInterface>`, :doc:`eHostess.PyConTextInterface <PyConTextInterface>`, etc.
3. Modules that analyze annotation data, using eHostess.Annotations objects as input.

The eHostess source code can be found here_ on GitHub. See the README file for more information.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Annotations
   eHostInterface
   PyConTextInterface
   MongoDBInterface
   Analysis

Examples
========

The following code snippet demonstrates how to run PyConText on a directory of notes and compare the result to a collection of annotations contained in a set of '.knowtator.xml' files. It also shows how to use the :doc:`Analysis` modules to analyze the result and output a TSV file.

.. literalinclude:: Example1.py

See :meth:`ConvertComparisonToTSV <eHostess.Analysis.Output.ConvertComparisonsToTSV>` for more about the result of the comparison output.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _eHost: http://ehostdoc.com/
.. _PyConText: https://github.com/chapmanbe/pyConTextNLP
.. _here: https://github.com/MMontgomeryTaggart/CardioNLP
