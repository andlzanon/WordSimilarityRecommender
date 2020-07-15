import time
import math
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
import os.path


# generate submit files
def generateFiles(k: int, test_data: pd.DataFrame, movies_similarities: pd.DataFrame, user_item: pd.DataFrame,
                  items_mean: pd.DataFrame, global_mean: float):

    print("--- Training Time: %s seconds ---" % (time.time() - start_training_time))
    start_prediction_time = time.time()

    for index, row in test_data.iterrows():
        user_id = row[1]
        movie_id = row[2]
        try:
            num = 0
            denom = 0
            valid_n = 0
            # get row of neighbours, set similarity to itself as 0 in order to not get itself
            # and than get the max values
            i = 0
            sim = movies_similarities.loc[movie_id][:]
            sim.loc[movie_id] = 0
            sim = sim.sort_values(ascending=False)
            n = sim.index[i]
            similarity = sim.iloc[i]
            while valid_n != k and sum(sim) != 0:
                if not math.isnan(user_item.loc[user_id][n]):
                    # calculate prediction
                    num = num + (similarity * user_item.loc[user_id][n])
                    denom = denom + similarity
                    valid_n = valid_n + 1

                # set similarity to 0 because it was already used
                # get next biggest similarity
                sim.iloc[i] = 0
                i = i + 1
                n = sim.index[i]
                similarity = sim.iloc[i]

            # calculate prediction
            if denom != 0 and num != 0:
                rui = num / denom
                submit_file.loc[index] = [index, "{:.3f}".format(rui)]
            else:
                rui = items_mean.loc[movie_id]
                submit_file.loc[index] = [index, "{:.3f}".format(rui)]

        except KeyError:
            rui = global_mean
            submit_file.loc[index] = [index, "{:.3f}".format(rui)]

    print("--- Prediction Time: %s seconds ---" % (time.time() - start_prediction_time))
    file_name = "submit_file_wordsim_knn_" + str(k) + ".csv"
    submit_file.to_csv(file_name, mode='w', header=submit_columns, index=False)
    print("--- File Created: %s ---" % file_name)


# generate similarity between movies i and j by calling
# Wu-Palmer Similarity with wordnet
def similarity_ij(n_aspects: int, aspects_i: list, aspects_j: list):
    sum = 0
    n_tuples = 0
    for i in range(0, n_aspects):
        sim = wn.wup_similarity(aspects_i[i], aspects_j[i])
        if sim is not None:
            sum = sum + (sim * (n_aspects - i))
            n_tuples = n_tuples + (n_aspects - i)

    if n_tuples > 0:
        return sum / n_tuples
    else:
        return 0


# get n (number) aspects most important to the movie that
# has a meaning on wordnet
def get_n_aspects(number: int, aspects_movie: pd.DataFrame):
    n = 0
    index = 0
    output = []
    while n < number:
        syns = wn.synsets(aspects_movie.iloc[index][0])
        if len(syns) > 0:
            output.append(syns[0])
            n = n + 1
        index = index + 1

    return output


# generate movie x movie similarity matrix by accessing its document with aspects and comparing the words with wordnet
def generate_sim_matrix(n_aspects: int, user_item_m: pd.DataFrame):
    sim_movies = pd.DataFrame(0, index=range(1, user_item.columns.max()), columns=range(1, user_item.columns.max()))
    nltk.download('wordnet')
    columns = ['aspect', 'score']

    for movie_i in range(1, user_item_m.columns.max() + 1):
        filename_mi = "../results/movie_" + str(movie_i) + ".csv"
        if os.path.isfile(filename_mi):
            aspects_movie_i = pd.read_csv(filename_mi, usecols=columns).sort_values('score', ascending=False)
            top_aspects_movie_i = get_n_aspects(n_aspects, aspects_movie_i)
            for movie_j in range(movie_i, user_item_m.columns.max() + 1):
                filename_mj = "../results/movie_" + str(movie_j) + ".csv"
                if os.path.isfile(filename_mj):
                    aspects_movie_j = pd.read_csv(filename_mj, usecols=columns).sort_values('score', ascending=False)
                    top_aspects_movie_j = get_n_aspects(n_aspects, aspects_movie_j)
                    sim_ij = similarity_ij(n_aspects, top_aspects_movie_i, top_aspects_movie_j)
                    sim_movies.loc[movie_i, movie_j] = sim_ij
                    sim_movies.loc[movie_j, movie_i] = sim_ij
                    print("sim between " + str(movie_i) + " and " + str(movie_j) + " is: " + str(sim_ij))

    return sim_movies


# start counting train time, get train_data from data set and delete timestamp column
start_training_time = time.time()
np.seterr(all='raise')
print("--- Start Time: %s seconds ---" % start_training_time)
used_columns = ['user_id', 'movie_id', 'rating']
train_data = pd.read_csv("../data-set/train_data .csv", usecols=used_columns)

# train means returns the average of user_id, movie_id and ratting
train_means = train_data.mean(axis=0)
global_mean = train_means[2]

# generate user/item matrix and mean item
user_item = train_data.pivot(index="user_id", columns="movie_id", values="rating")
items_mean = user_item.mean(axis=0)

# sim_matrix = generate_sim_matrix(10, user_item)
# sim_matrix.to_csv("sim_matrix10.csv", mode='w', header=False, index=False)
sim_matrix = pd.read_csv("./sim_matrix.csv", names=range(1, user_item.columns.max() + 1))
sim_matrix.index += 1

# create submit file, a csv with the layout requested
test_data = pd.read_csv("../data-set/test_data.csv")
submit_columns = ['id', 'rating']
submit_file = pd.DataFrame(columns=submit_columns)

# generate submit file by getting the average rating from movie_average
# try catch because there is a film that was not rated by any user
for k in range(24, 40, 2):
    generateFiles(k, test_data, sim_matrix, user_item, items_mean, global_mean)
