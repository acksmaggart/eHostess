from pyConTextNLP import pyConTextGraph as pyConText
from pyConTextNLP.helpers import sentenceSplitter
import pyConTextNLP.itemData as itemData
from SentenceRepeatManager import SentenceRepeatManager
from SentenceReconstructor import SentenceReconstuctor
import re, os


defaultModifierToAnnotationClassMap = {
    "NEGATED_EXISTENCE" : "bleeding_absent",
    "AFFIRMED_EXISTENCE" : "bleeding_present"
}

defaultTargetFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/targets.tsv'
defaultModifiersFilePath = os.path.dirname(__file__) + '/TargetsAndModifiers/modifiers.tsv'

class PyConTextInferface:
    def __init__(self):
        self.stuff = "stuff"


    @classmethod
    def annotateSingleDocument(cls, documentFilePath, targetFilePath=defaultTargetFilePath,
                               modifiersFilePath=defaultModifiersFilePath, sentenceSplitter=sentenceSplitter,
                               modifierToClassMap=defaultModifierToAnnotationClassMap):

        targets = itemData.instantiateFromCSVtoitemData(targetFilePath)
        modifiers = itemData.instantiateFromCSVtoitemData(modifiersFilePath)

        inFileHandle = open(documentFilePath, 'r')
        noteBody = inFileHandle.read()
        inFileHandle.close()

        repeatManager = SentenceRepeatManager()
        sentenceReconstructor = SentenceReconstuctor(noteBody)
        sentences = sentenceSplitter().splitSentences(noteBody)
        pyConTextMarkups = []

        for sentence in sentences:

            matches = re.findall(re.escape(sentence), noteBody)
            span = None
            if not matches:
                print("eHostess/PyConTextInterface/PyConText: Did not find sentence in text, something is wrong.")
                print("Note: %s" % documentFilePath)
                print("Sentence:")
                print(sentence + '\n')
                exit(1)

            # if the sentence appears multiple times in the note we need to make sure we grab them all instead of grabbing
            # the first one multiple times.
            if len(matches) > 1:
                span = repeatManager.processSentence(sentence, noteBody)

            else:
                # if there is only once instance of the sentence, proceed as normal
                match = re.search(re.escape(sentence), noteBody)
                start = match.start()
                end = match.end()
                span = (start, end)

            markup = pyConText.ConTextMarkup()
            markup.setRawText(sentence)
            markup.cleanText()
            markup.markItems(modifiers, mode="modifier")
            markup.markItems(targets, mode="target")
            markup.pruneMarks()
            markup.applyModifiers()
            markup.pruneSelfModifyingRelationships()
            markup.dropInactiveModifiers()

            print "Hi!"

