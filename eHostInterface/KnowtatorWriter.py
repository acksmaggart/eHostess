#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 11:02:49 2017

@author: Originally written by Alec Chapman; edited by Danielle Mowery
"""

import os
import uuid
import datetime
import time

from xml.etree.cElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom


# from lxml import etree
# from twisted.persisted.aot import prettify

class mentionAnnotation(object):
    def __init__(self, tagObject, textSource=None, mentionClass=None, mentionid=None, annotatorid='pyConText_FINDER',
                 span=None, start=None, end=None,
                 spannedText=None, creationDate=None, XML=None, MentionXML=None):
        """Creates an annotation of Object"""
        self.textSource = textSource
        self.mentionid = str(mentionid)
        self.mentionClass = mentionClass
        self.annotatorid = annotatorid
        self.span = span
        self.start = start
        self.end = end
        self.spannedText = spannedText
        self.creationDate = creationDate
        self.XML = XML
        self.MentionXML = MentionXML
        self.setCreationDate()
        self.setXML()
        self.setMentionXML()

    def setTextSource(self, textSource):
        """Sets the text for spannedText"""
        self.textSource = textSource

    def setText(self, text):
        """Sets the text for spannedText"""
        self.spannedText = text

    def setSpan(self, markupSpan):
        self.span = markupSpan

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def setMentionID(self, ID):
        self.mentionid = str(ID)

    def setCreationDate(self):
        self.creationDate = time.strftime("%c")  # add time zone

    def setXML(self):
        """Creates an element tree that can later be appended to a parent tree"""
        annotation_body = Element("annotation")
        mentionID = SubElement(annotation_body, 'mention')
        mentionID.set('id', self.getMentionID())  # perhaps this needs to follow eHOST's schema
        annotatorID = SubElement(annotation_body, "annotator")
        annotatorID.set('id', 'eHOST_2010')
        annotatorID.text = self.getAnnotatorID()
        start = self.getSpan()[0];
        end = self.getSpan()[1]
        print start, end
        # span = SubElement(annotation_body, "span",{"start":str(start),"end":str(end)}) #Why is this backwards?
        spannedText = SubElement(annotation_body, 'spannedText')
        spannedText.text = self.getText()
        creationDate = SubElement(annotation_body, "creationDate")
        creationDate.text = self.getCreationDate()
        self.XML = annotation_body
        # print(prettify(parent))

    def setMentionXML(self):
        classMention = Element("classMention")
        classMention.set("id", self.getMentionID())
        mentionClass = SubElement(classMention, "mentionClass")
        mentionClass.set("id", self.getMentionClass())
        mentionClass.text = self.getText()
        self.MentionXML = classMention

    def getTextSource(self):
        return self.textSource

    def getMentionClass(self):
        return self.mentionClass

    def getMentionID(self):
        return self.mentionid

    def getText(self):
        return self.spannedText

    def getSpan(self):
        return self.span

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getAnnotatorID(self):
        return self.annotatorid

    def getCreationDate(self):
        return self.creationDate

    def getXML(self):
        return self.XML

    def getMentionXML(self):
        return self.MentionXML

    def stringXML(self):
        def prettify(elem):
            """Return a pretty-printed XML string for the Element.
            """
            rough_string = ElementTree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")

        XML_string = prettify(self.getXML())
        MentionXML_string = prettify(self.getMentionXML())
        return XML_string + MentionXML_string


def createAnnotation(ct, file_name, term, span, mention_class):  # eventually mention_class will be defined by the logic
    """Takes a ConTextMarkup object and returns a list of annotation object"""

    annotation = mentionAnnotation(tagObject=ct, textSource=file_name, mentionClass=mention_class,
                                   mentionid=ct, spannedText=term,
                                   span=eval(span), start=eval(span)[0], end=eval(span)[1])  # MADE THIS THE DOCSPAN

    start, end = eval(span)
    annotation.setTextSource(file_name + ".txt")
    annotation.setText(term)
    annotation.setSpan(span)
    annotation.setStart(start)
    annotation.setEnd(end)
    annotation.setMentionID(ct)

    # print annotation.stringXML()


    return annotation


def writeKnowtator(annotations, save_dir, text_source):  # test_source should be read automatically from the XML string
    """Writes a .txt.knowtator.xml file for all annotations in a document
    Takes a list of mentionAnnotation objects, a source file name, and an outpath.
    2/3/17: returns a single ElementTree Element object.
    Need to be able to turn this into a string."""

    docOut = "";
    outString = ""
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    print text_source
    #     with open(os.path.join(outpath,text_source+'.knowtator.xml'),'w') as f0:
    #         f0.write(XMLstring)
    #     f0.close()
    #     return os.path.join(outpath,text_source+'.knowtator.xml')

    fout = open("%s/%s-PyConText.knowtator.xml" % (save_dir, text_source), "w")
    outString = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    outString += """<annotations textSource="%s">\n""" % text_source
    docOut = outString;
    annotXML = ""
    ct = 1
    for annotation in annotations:
        outString = ""
        outStringClsMent = ""
        start = str(annotation.getStart());
        end = str(annotation.getEnd())

        # print classAnnot;raw_input()
        outString += """    <annotation>\n"""
        outString += """        <mention id="pyCONTEXT_Instance_%s" />\n""" % str(ct)
        outString += """        <annotator id="01">%s</annotator>\n""" % annotation.getAnnotatorID()
        outString += """        <span start="%s" end="%s" />\n""" % (start, end)
        outString += """        <spannedText>%s</spannedText>\n""" % annotation.getText()
        outString += """        <creationDate>%s</creationDate>\n""" % time.strftime("%c")
        outString += """    </annotation>\n"""

        # create Knowtator mention class


        outStringClsMent += """    <classMention id="pyCONTEXT_Instance_%s">\n""" % str(ct)
        outStringClsMent += """        <mentionClass id="%s">%s</mentionClass>\n""" % (
        annotation.getMentionClass(), annotation.getText())
        outStringClsMent += """    </classMention>\n"""

        ct += 1
        a = outString + outStringClsMent
        annotXML += a
        # print annotXML  # ;raw_input()
    docOut += annotXML
    outString = ""

    footer = """    <pyCONTEXT_Adjudication_Status version="1.0">\n"""
    footer += """        <Adjudication_Selected_Annotators version="1.0" />\n"""
    footer += """        <Adjudication_Selected_Classes version="1.0" />\n"""
    footer += """        <Adjudication_Others>\n"""
    footer += """            <CHECK_OVERLAPPED_SPANS>true</CHECK_OVERLAPPED_SPANS>\n"""
    footer += """            <CHECK_ATTRIBUTES>true</CHECK_ATTRIBUTES>\n"""
    footer += """            <CHECK_RELATIONSHIP>false</CHECK_RELATIONSHIP>\n"""
    footer += """            <CHECK_CLASS>true</CHECK_CLASS>\n"""
    footer += """            <CHECK_COMMENT>false</CHECK_COMMENT>\n"""
    footer += """        </Adjudication_Others>\n"""
    footer += """    </pyCONTEXT_Adjudication_Status>\n"""
    footer += """</annotations>"""

    fout.write(docOut + footer)
    fout.close()  # ;raw_input()

# def main():
#
#    docAnnots={}
#
#    lines=open(os.getcwd()+"/src/reportsOutput/eHOST_annotations.txt","r").readlines()
#    for l in lines[1:]:
#        fnameExt, fname, term, span, clas = l.strip().split("\t")
#        if fname in docAnnots.keys():
#            docAnnots[fname]+=[(term, span, clas)]
#        else:
#            docAnnots[fname]=[(term, span, clas)]
#
#
#    for doc in docAnnots:
#        createdAnnots=[]; ct=1
#        annots=docAnnots[doc]
#        for a in annots:
#            an=createAnnotation(str(ct), doc, a[0], a[1], a[2])
##             print an.getMentionID()
##             print an.getSpan()
##             print an.getText()
##             print an.getMentionClass()
#            createdAnnots.append(an)
#            ct+=1
#        writeKnowtator(createdAnnots, doc)#;raw_input()
#
#
#
# if __name__=='__main__':
#
#    main()





