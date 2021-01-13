import xml.etree.ElementTree as ET

DATA = "./lib/data/config.xml"

mytree = ET.parse(DATA)
myroot = mytree.getroot()


def write():
    mytree.write(DATA)

