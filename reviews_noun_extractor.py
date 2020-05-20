import xml.etree.ElementTree as ET
import collections
from itertools import chain
import os
from datetime import datetime


def reviews_noun_extractor(dir_target, destination_file):

    """Extracts all the nouns in all the reviews of the reviews dataset

    Args:
        dir_target(str): The directory that contain the ".xml" files with the reviews

        destination_file(str): The ".txt" file that will contain all the nouns extracted
        from the reviews

    Returns:
        None
    """
    
    #tags for nouns:
    desired_POS=["NN", "NNS", "NNP", "NNPS"] 
    
    #clear file, in case it already exists:
    open(destination_file, 'w').close() 

    #trasversing all the ".xml" files of the database:
    for file in os.listdir(dir_target):
        current_directory = os.path.join(dir_target, file)
        single_review_noun_extractor(current_directory, desired_POS, destination_file)  
       

def single_review_noun_extractor(file_name, desired_POS, destination_file):

    """Extracts all the nouns contained in each ".xml" file of the reviews dataset,
        given a certain grammatical class.
        PEN treebank POS-tags for nouns are available at:  
        https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html

    Args:
        file_name(str): The ".xml" file to be parsed
        
        desired_POS (list): A list containing the tags for nouns;
        desired_POS=["NN", "NNS", "NNP", "NNPS"] 

        destination_file (str): This ".txt" file will contain all the nouns
        extracted from all the reviews in the dataset

    Returns:
        None
    """
    tree = ET.parse(file_name)
    root = tree.getroot()
    
    #find all elements of the xml tree that is labeled as "sentence":
    element = root.findall(".//sentence")

    desired_tokens = []

    for sentence in element:
        #find all the tokens in the xml tree:
        sentence.findall(".//token")
        for tokens in sentence:
            for token in tokens:
                #<word> and <POS> are children of the tolken element:
                for token_child in token: 
                    #appends if the desired tag is "POS" and it's content "text" is a noun:
                    if token_child.tag =="POS" and token_child.text in desired_POS:
                        desired_tokens.append(token)
                        
    desired_nouns=[]

    #content is a token of the xml tree:
    for content in desired_tokens:
        #content_child is a token_child of the xml tree
        for content_child in content:
            #appends the word attribute(noun) contained in content:
            if content_child.tag == "word":
                #content_child_text is a word which grammatical class is noun:
                content_child_text = content_child.text.lower()
                desired_nouns.append(content_child_text)
              

    with open(destination_file, 'a+', encoding="utf-8") as f:
        print(' '.join(desired_nouns), file=f)



if __name__ == '__main__':

    #dirtest = "C:\\Users\\User\\Desktop\\ic\\Reviews\\HetRec_CoreNLP" 
    dirtest = "your diretory"
    destiny_file = "corpora_reviews.txt"
    
    reviews_noun_extractor(dirtest, destiny_file)
