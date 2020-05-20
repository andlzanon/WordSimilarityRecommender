import xml.etree.ElementTree as ET
import collections
from itertools import chain
import os 

def BNC_noun_parser (xml_name, 
                     desired_tag,           
                     searched_token,        
                     first_attribute,       
                     second_attribute,     
                     file_destiny):         

    """This function extracts all the present nouns in the current xml file.
        The nouns are stored in lower case.

    Args:
        xml_name (str): The current xml file to be parsed

        desired_tag (str): The tag should be passed as "w", since this is 
        the tag to be found in the BNC xml 
        
        searched_token (str): The token should be passed as "pos", since 
        the token we are looking for in the BNC xml tree is "pos". 

        first_attribute (str): The attribute should be passed as "SUBST", since
        this is the grammatical class we are looking for in the BNC xml tree.
        The type of tagging for nouns are available in this link:
        http://www.natcorp.ox.ac.uk/docs/gramtag.html

        second_attribute (str): This attribute should be passed as "hw"

        file_destiny (str): This parameter should be passed as the name of the
        ".txt" file that is going to store the parsed nouns

    Returns:
        None
    """                                                             
                                                                                                                                   
    tree = ET.parse(xml_name)
    root = tree.getroot()

    tag_parameter = ".//" + desired_tag

    # finds only elements with the tag "w" which
    #are direct children of the current root:
    element = root.findall(tag_parameter)

    #list that is going to contain all the nouns extracted form the BNC file;
    #if the pos-tagging is a noun(pos="SUBST"), it is stored in the parsed_tokens list
    parsed_tokens = []
       
    
    for desired_tag in element:
        #current_attribute represents the grammatical class of the word traversed in the BNC xml tree
        current_attribute = desired_tag.attrib[searched_token]

        #if the grammatical class represents a noun, then the noun should be appended to the list
        if current_attribute == first_attribute: 
            
            #the desired nouns are attributes of 'hw'
            found_noun = desired_tag.attrib[second_attribute] 

            #set the noun to lower case:   
            found_noun = found_noun.lower()
            parsed_tokens.append(found_noun)

    #print the found nouns in the ".txt" file:
    with open(file_destiny, 'a+', encoding="utf-8") as destiny:
        print(' '.join(parsed_tokens), file=destiny)

    


def BNC_nouns_extractor(root_directory, file_destiny):

    """Trasverse the folder "Texts" contained in the BNC database. The folder
    "Texts" contains the xml files of the database, which nouns are going
    to be extracted and written in "corpora_BNC.txt"

    Args:
        root_directory (str): The directory on your computer for the folder
        "Texts" that was downloaded from BNC database

        file_destiny (str): A ".txt" file that is going to contain all the
        parsed nouns

    Returns:
        file_destiny (str): The ".txt" file that contains the extracted nouns
    
    """    
    #the below line clears the file:
    open(file_destiny, 'w').close() 

    for subdir, dirs, files in os.walk(root_directory):
        for file in files:                      
            xml_file = os.path.join(subdir, file)
            BNC_noun_parser(xml_file, "w", "pos", "SUBST", "hw", file_destiny)

    return (file_destiny)


#test:
if __name__ == '__main__':

    file_destiny = "corpora_BNC.txt"
    #root_directory = "C:\\Users\\User\\Desktop\\ic\\ota_20.500.12024_2554\\2554\\Texts"
    root_directory = "Your directory"

    BNC_nouns_extractor(root_directory, file_destiny)


