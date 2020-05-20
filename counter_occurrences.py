import collections
from itertools import chain

def count_in_file(filename_origin):

    """Given the ".txt" file that contains all the nouns parsed, this function
    counts the number of occurences of each noun of the file

    Args:
        filename_origin (str): file that contains the parsed nouns.
        In this case, "corpora_BNC.txt" or "corpora_reviews.txt"

    Returns:
        counted_nouns (Counter): A mapping between the noun and it's number of occurences

    """
    #reads the file and count the number of occurences of each noun:
    with open(filename_origin, 'r', encoding="utf-8") as f:
        #counted_nouns is a kind of mapping between the strings of the file (noun)
        #and it's occurence; example: {'film': 86286, ...,'movie': 80667}
        counted_nouns = collections.Counter(chain.from_iterable(map(str.split, f)))
        return (counted_nouns)


def counter_occurences(filename_origin, counting_file):

    """Given the ".txt" file that contains all the nouns parsed, this function
    counts the number of occurences of each noun of the file and prints
    in the counting_file the mapping done between each noun and it's occurrence

    Args:
        filename_origin (str): file that contains the parsed nouns.
        In this case, "corpora_BNC.txt" or "corpora_reviews.txt"

        counting_file (str): The ".txt" file that is going to contain 
        the mapping between the noun and it's occurrences

    Returns:
        None
    """
    counted_nouns = count_in_file(filename_origin)

    with open(counting_file, 'w', encoding="utf-8") as f:
        print(counted_nouns, file=f)

#tests:
if __name__ == '__main__':
   
    counter_occurences("corpora_BNC.txt", "BNC_counter.txt")
    counter_occurences("corpora_reviews.txt", "counter_review.txt")