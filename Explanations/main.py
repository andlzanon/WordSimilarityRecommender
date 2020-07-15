import time
import math
import os.path
from random import randrange
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn


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


# calculate the prediction of a user movie tuple considering k neighbours
def calculate_prediction(k: int, user: int, movie: int, item_mean_m: pd.DataFrame, sim_matrix_m: pd.DataFrame,
                         user_item_m: pd.DataFrame, gm: float):
    try:
        num = 0
        denom = 0
        i = 0
        valid_n = 0
        sim = sim_matrix_m.loc[movie][:]
        sim.loc[movie] = 0
        sim = sim.sort_values(ascending=False)
        n = sim.index[i]
        similarity = sim.iloc[i]
        while valid_n != k and sum(sim) != 0:
            if not math.isnan(user_item_m.loc[user][n]):
                # calculate prediction
                num = num + (similarity * user_item_m.loc[user][n])
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
        else:
            rui = item_mean_m.loc[movie_id]

    except KeyError:
        try:
            rui = item_mean_m.loc[movie_id]
        except KeyError:
            rui = gm

    return rui


def generate_explanations(profile_itens: pd.DataFrame, top_item: int, movie_data_info: pd.DataFrame):
    i = 0
    columns = ['aspect', 'score']
    filename_rec = "../results/movie_" + str(top_item) + ".csv"
    if os.path.isfile(filename_rec):
        aspects_rec_movie = pd.read_csv(filename_rec, usecols=columns).sort_values('score', ascending=False)
        top_rec_aspects = get_n_aspects(5, aspects_rec_movie)
        max = 0
        word_p = ""
        word_r = ""
        movie_pro = 0
        while profile_itens.iloc[i] >= 4:
            p_movie = profile_itens.index[i]
            filename_profile = "../results/movie_" + str(p_movie) + ".csv"
            if os.path.isfile(filename_profile):
                aspects_profile_movie = pd.read_csv(filename_profile, usecols=columns).sort_values('score',
                                                                                                   ascending=False)
                top_profile_aspects = get_n_aspects(5, aspects_profile_movie)

                for p_aspects in top_profile_aspects:
                    for r_aspects in top_rec_aspects:
                        sim = wn.wup_similarity(p_aspects, r_aspects)
                        if sim is not None and sim > max:
                            max = sim
                            movie_pro = p_movie
                            word_p = p_aspects.name().split('.')[0]
                            word_r = r_aspects.name().split('.')[0]

            i = i + 1

    else:
        return "Because you rated well the movie \"" + movie_data_info.loc[top_item][0] + "\" watch \"" + \
               movie_data_info.loc[profile_itens.index[0]][0] + "\""

    movie_pro_name = movie_data_info.loc[movie_pro][0]
    movie_rec_name = movie_data_info.loc[top_item][0]
    print(movie_pro_name)
    print(movie_rec_name)

    if word_p != word_r:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the similar word \"" + word_r + "\""
    else:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the same word"

    return sentence


def get_top_explainable(top_reted: pd.DataFrame):
    n = 0
    i = 0
    output = []
    while n < 5:
        filename = "../results/movie_" + str(top_reted.index[i]) + ".csv"
        if os.path.isfile(filename):
            output.append(top_reted.index[i])
            n = n + 1

        i = i + 1

    return output


# start counting train time, get train_data from data set and delete timestamp column
start_training_time = time.time()
np.seterr(all='raise')
nltk.download('wordnet')
print("--- Start Time: %s seconds ---" % start_training_time)
used_columns = ['user_id', 'movie_id', 'rating']
train_data = pd.read_csv("../data-set/train_data .csv", usecols=used_columns)

# train means returns the average of user_id, movie_id and ratting
train_means = train_data.mean(axis=0)
global_mean = train_means[2]

# generate user/item matrix and mean item
user_item = train_data.pivot(index="user_id", columns="movie_id", values="rating")
items_mean = user_item.mean(axis=0)

# get similarity matrix from file
sim_matrix = pd.read_csv("./sim_matrix.csv", names=range(1, user_item.columns.max()))
sim_matrix.index += 1

users = []
for i in range(0, 10):
    users.append(randrange(1, user_item.columns.max()))

data_cols = ['movie_id', 'title']
movie_data = pd.read_csv("../data-set/movies_data.csv", usecols=data_cols)
movie_data.set_index('movie_id', inplace=True)

file = open("explanations2.txt", "w")
for u in users:
    profile = user_item.loc[u][:]
    if len(profile) > 0:
        rated = profile.dropna().sort_values(ascending=False)
        predictions = pd.DataFrame(0, index=user_item.columns, columns=['rating'])
        for movie_id in user_item.columns:
            if movie_id not in rated.index:
                predictions.loc[movie_id] = calculate_prediction(20, u, movie_id, items_mean, sim_matrix, user_item,
                                                                 global_mean)
            else:
                predictions.loc[movie_id] = 0

            print(movie_id)

        top = predictions.sort_values(by='rating', ascending=False)
        top_explainable = get_top_explainable(top)
        print("--- Prediction Time: %s seconds ---" % (time.time() - start_training_time))
        start_training_time = time.time()
        file.write("----- INIT USER " + str(u) + " ----- \n")
        file.write("----- TOP RATED PROFILE ----- \n")
        i = 0
        while rated.iloc[i] >= 4:
            file.write(str(movie_data.loc[rated.index[i]][0]) + "\n")
            i = i + 1
        file.write("----- RECOMMENDED ----- \n")
        for m in top_explainable:
            file.write(str(movie_data.loc[m][0]) + "\n")
        file.write("----- EXPLANATIONS ----- \n")
        for movie_rec in top_explainable:
            explanation = generate_explanations(rated, movie_rec, movie_data)
            print(explanation)
            file.write(explanation + "\n")
        file.write("----- END " + str(u) + " ----- \n\n")

file.close()
