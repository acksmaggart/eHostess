# eHostess
### The Extra Helpful, Overly Syntactic, Thoroughly Enjoyable Software Suite
###### (And Companion to [eHost][1])

The guiding assumption of this package is that there may be multiple annotation sources, e.g. eHost, PyConText, machine learning algorithms, but that the annotations produced by all the sources share common attributes such as a source document name, text span, annotation class, etc. The second assumption is that the reason we are producing annotations is to compare the annotations produced by different methods and to calculate arbitrary annotation metrics. Given these two assumptions, the proposed design of this package is to build a central set of classes that represent abstract notation objects that contain information about their source, but are otherwise totally generic to allow comparison between annotations produced by different sources. These objects may then be analyzed to produce the desired metrics. In addition to the modules that describe annotation objects and their analysis there will be a set of modules to generate annotation objects from different sources. For example, a module to bring in annotations from eHost, a module to generate annotations using PyConText, etc. Using this structure any ideosyncracies in annotation sources will be handled by classes that bring in annotations from that source.

Package Structure:
The package will have the following modules.
1. Annotation: A module containing classes that represent annotaion objects including mention-level annotations, and whole documents.
2. Analysis: A module containing analysis logic that operates on the annotation objects in module 1.
3. A module for each annotation source. For example one for eHost and one for PyConText. These modules will bear the name of the source with which they interface followed by the word "Interface".
4. NotePreprocessing: A module containing tools to manipulate text notes, usually in preparation for manual annotation in eHost.
5. DevelopmentAids: This module cantains content that is useful for developers such as example `.knowtator` files, sample cardiology notes, eHost annotation schemas, etc.
6. UnitTestDependencies: This directory contains files that are necessary to run the tests in the `UnitTests.py` module.

Project documentation can be found at [ehostess.readthedocs.io][2].
The package also contains a `Documentation` directory whose contents can be used to produce HTML documentation pages using sphinx. To generate the documentation simply execute `make html` in the Documentation directory after installing sphinx. After executing `make` the documentation may then be found in the `Documentation/_build/` directory.

[1]: http://ehostdoc.com/
[2]: http://ehostess.readthedocs.io