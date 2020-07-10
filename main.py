import nltk
import collections
import module.ocurrences as count_occur
import module.kl as kl
import corenlp
import pandas as pd

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
# TODO We need four tuples
# reviews -> ri
# aspect in review -> aij
# relevance of a aspect in review -> relevance (aij, ri) obtained with KL divergence
# sentment of a aspect in review -> sent(aij, ri) obtained with CoreNLP

# First, we need extract the nouns of the review with POS-tagging algorithm.
# So we need count the numbe of occurrences of term (t) in corpus (c or reviews) -> p(t, ca) and p(t, cb).
# Then we calcule the KL divergence between terms of reviews and BNC.
# The terms with greater KL divergence is labeled aspect and his score is the relevance

# Finally, we also run a sentment analysis algorithm (CoreNLP)

def kl_nouns_divergence(count_nouns_BNC, count_nouns_reviews):
    KL_values = {}

    for noun in count_nouns_reviews:
        frequency_corpora_reviews = count_nouns_reviews[noun] 
        frequency_corpora_BNC = count_nouns_BNC[noun]
        KL_values[noun] = kl.divergence(frequency_corpora_reviews, frequency_corpora_BNC)

    return KL_values

def sentimtent_analysis(review: str, terms: dict, client):
    ann = client.annotate(review)
    terms = {t: {"relevance": terms[t], "sentiment": 0 } for t in terms}
    for s in ann.sentence:
        sentiment = s.annotatedParseTree.sentiment
        words = [t.word.lower() for t in s.token if (t.pos == 'NN' or t.pos == 'NNP' or t.pos == 'NNS' or t.pos == 'NNPS')]
        for term in terms:
            if term in words:
                if terms[term]["sentiment"] < sentiment:
                    terms[term]["sentiment"] = sentiment
    return terms

def top_terms(dict_kl: dict):
    r = {}
    for item in dict_kl:
        if dict_kl[item] == float("inf"):
            r[item] = 1000
            continue
        if dict_kl[item] > 0:
            r[item] = dict_kl[item]
    return r

def aspect_score(aspect: dict):
    sum_num = 0
    sum_dem = 0
    for r in aspect:
        sum_num += aspect[r]["occurs"] * aspect[r]["aspect"]["relevance"] * aspect[r]["aspect"]["sentiment"]
        sum_dem += 1
    if sum_dem == 0:
        return 0
    return (sum_num/sum_dem)

def extract_nouns(review: str):
    tokens = nltk.word_tokenize(review.lower())
    tagged = nltk.pos_tag(tokens)
    return [word for word,pos in tagged if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]

def kl_divergence(nouns: list, bnc_path = "datasets/corpora_BNC.txt"):
    count_nouns_BNC = count_occur.count_in_file(bnc_path)
    counted_nouns = collections.Counter(nouns)
    return kl_nouns_divergence(count_nouns_BNC, counted_nouns), counted_nouns

def aspect_extraction(review: str, client):
    nouns = extract_nouns(review)
    dict_kl, counted_nouns = kl_divergence(nouns)
    aspects = top_terms(dict_kl)
    aspects = sentimtent_analysis(review, aspects, client)
    return aspects, counted_nouns

client = corenlp.CoreNLPClient(start_server=False, annotators=['sentiment'], timeout = 30000)

mv = pd.read_csv('datasets/movie_reviews.csv')

groups = mv.groupby(["movie_id"]).groups

for movie in groups:
    reviews_aspects = {}
    for r in groups[movie]:
        try:
            aspects, counted_nouns = aspect_extraction(mv["text"][r], client)
            for aspect in aspects:
                if aspect not in reviews_aspects:
                    reviews_aspects[aspect] = {}
                reviews_aspects[aspect][r] = {"occurs": counted_nouns[aspect], "aspect": aspects[aspect]}
        except:
            print("Erro na revisao {0}, filme {1}".format(r, movie))
            continue
        
    top_aspects = [[aspect, aspect_score(reviews_aspects[aspect])] for aspect in reviews_aspects]
    df = pd.DataFrame(data=top_aspects, columns=["aspect", "score"])
    df = df.sort_values(by=['score'], ascending=False)
    df.to_csv("results/movie_" + str(movie) + ".csv", index=False)