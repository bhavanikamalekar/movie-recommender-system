import pickle
movies = pickle.load(open("movies_list.pkl", "rb"))
print(movies.head())
