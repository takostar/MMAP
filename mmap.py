# coding=utf-8
'''
@Author: tako star
@Date: 2020-05-09 10:36:37
@LastEditors: tako star
@LastEditTime: 2020-05-09 20:40:36
'''
from re import split
import random
from bs4 import BeautifulSoup
# from nltk import clean_html
import xml.etree.ElementTree as ET
ap = '{http://schemas.mindjet.com/MindManager/Application/2003}'


def genOId():
    OId = ''.join(
        random.sample(
            'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba0123456789',
            22))
    return OId + '=='


def genText(Element, text):
    Text = Element.find('./{}Text'.format(ap))
    if (Text is None):
        Text = ET.SubElement(Element, '{}Text'.format(ap))
    Text.set('Dirty', '0000000000000001')
    Text.set('PlainText', text)
    Text.set('ReadOnly', 'false')
    ET.SubElement(Text, '{}Font'.format(ap))


def genSubtopic(Topic, text):
    SubTopics = Topic.find('./{}SubTopics'.format(ap))
    if (SubTopics is None):
        SubTopics = ET.SubElement(Topic, '{}SubTopics'.format(ap))
    TopicViewGroup = Topic.find('./{}TopicViewGroup'.format(ap))
    if (TopicViewGroup is None):
        TopicViewGroup = ET.SubElement(Topic, '{}TopicViewGroup'.format(ap),
                                       {"ViewIndex": "0"})
    elif (TopicViewGroup.find('./{}Collapsed'.format(ap)) is None):
        ET.SubElement(TopicViewGroup, '{}Collapsed'.format(ap), {
            "Collapsed": "false",
            "Dirty": "0000000000000001"
        })
    SubTopic = ET.SubElement(SubTopics, '{}Topic'.format(ap))
    # TopicViewGroup ViewIndex="0"
    ET.SubElement(SubTopic, '{}TopicViewGroup'.format(ap), {"ViewIndex": "0"})
    SubTopic.set('Dirty', '0000000000000001')
    SubTopic.set('OId', genOId())
    SubTopic.set('Gen', '0000000000000000')
    genText(SubTopic, text)


def notesToTopic(Topic):

    # *传入topic标签,将其中的notes便签转化成topic添加到subtopic中
    # notes中的换行 &lt;br&gt;
    # notes = Topic.findall('./{}NotesGroup/{}NotesXhtmlData'.format(ap, ap))
    notes = Topic.find('./{}NotesGroup/{}NotesXhtmlData'.format(ap, ap))

    if (notes is not None):
        html = notes[0]
        # html = NotesXhtmlData[0]
        html_str = ET.tostring(html)
        html_str = ''.join(BeautifulSoup(html_str, 'lxml').get_text())
        subtopics = html_str.split('\n')
        # 添加子topic
        for subtopic in subtopics:
            if (len(subtopic) > 0):
                genSubtopic(Topic, subtopic)
    else:
        return


def notesPrevToTopic(Topic):
    notes = Topic.find('./{}NotesGroup/{}NotesXhtmlData'.format(ap, ap))
    if (notes is not None):
        attrib = notes.attrib
        if ("PreviewPlainText" in attrib):
            PreviewPlainText = attrib["PreviewPlainText"]
            textList = split('<br>|。|  ', PreviewPlainText)
        for text in textList:
            if (len(text) > 0):
                genSubtopic(Topic, text)


def proXml(path):
    tree = ET.parse(path)
    # root = tree.getroot()
    return tree


if __name__ == "__main__":
    tree = proXml('Document.xml')
    root = tree.getroot()
    Topics = root.findall('.//{}Topic'.format(ap))
    for Topic in Topics:
        # 引用,直接传入
        # notesToTopic(Topic)
        notesPrevToTopic(Topic)
    tree.write('output.xml', encoding='utf-8')