import xml.etree.ElementTree as ET

#file should be passed as 'BPA.xml', as an example
#the above function guarantees that the number of children of the tag 'w' is 
#the same number of the token 'pos=' counted in the file
#if this condition is not satisfied, the parser of nouns is going to be incorrect

def is_sucessfull(filename, element):

    with open(filename, 'r') as xml_file:
        current_read = xml_file.read()

    pos_count = current_read.count('pos=')

    #guarantees that the ocurrences of the children of tag 'w' is the same as the occurrences of the 
    #token 'pos='
    assert len(element) == pos_count

#the parameter xml_name should be passed as "BPA.xml", for example
def BNC_noun_parser(xml_name):
    
    tree = ET.parse(xml_name)
    root = tree.getroot()

    element = root.findall(".//w")# finds only elements with the tag "w" which are direct children of the current root

    is_sucessfull(xml_name, element)

    nouns_tokens=[]#list that is going to contain all the nouns extracted form the BNC file

    #if the pos-tagging is a noun(pos="SUBST"), it is stored in the nouns_tokens list
    #the type of tagging for nouns are available in this link: http://www.natcorp.ox.ac.uk/docs/gramtag.html
    
    for w in element:
        if w.attrib['pos'] == "SUBST": 
            nouns_tokens.append(w.attrib['hw'])#the desired noun is an attribute of 'hw'


    print(nouns_tokens)#to visualize the extracted nouns

if __name__ == "__main__":
    BNC_noun_parser('BPA.xml')