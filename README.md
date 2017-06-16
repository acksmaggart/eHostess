# eHostess
### The Extra Helpful, Overly Syntactic, Thoroughly Enjoyable Software Suite
### (And Companion to eHost)

The guiding assumption of this package is that there may be multiple annotation sources, e.g. eHost, PyConText, machine learning algorithms, but that the annotations produced by all the sources share common attributes such as a source document name, text span, annotation class, etc. The second assumption is that the reason we are producing annotations is to compare the annotations produced by different methods and to calculate arbitrary annotation metrics. Given these two assumptions, the proposed design of this package is to build a central set of classes that represent abstract notation objects that contain information about their source, but are otherwise totally generic to allow comparison between annotations produced by different sources. These objects may then be compared and analyzed to produce the desired metrics. In addition to this central set of classes there will be a set of classes for each annotation source. For example, a set of classes to bring in annotations from eHost, a set of classes to bring in annotations from PyConText, etc. Using this structure it will be easy to write generalized analysis logic to compare annotations without having to consider the differences in annotation source. Any ideosyncracies in annotation sources will be handled by classes that bring in annotations from that source.

Proposed package structure:
The package will have the following modules.
1. Annotation: A module containing classes that represent annotaion objects including mention-level annotations, and whole documents.
2. Analysis: A module containing analysis logic that operates on the annotation objects in module 1.
3. A module for each annotation source. For example one for eHost and one for PyConText. These modules will bear the name of the source with which they interface followed by the word "Interface".
4. NotePreprocessing: A module containing tools to manipulate text notes, usually in preparation for manual annotation in eHost.
