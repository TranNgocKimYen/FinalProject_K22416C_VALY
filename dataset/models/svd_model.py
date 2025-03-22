import pickle
import numpy as np
from surprise import Reader, Dataset, \
    SVD
from surprise.model_selection import cross_validate, GridSearchCV


from libs.reviewconnector import load_data

data=load_data()
new_df = data[['user_id', 'business_id', 'rating']]

# using Reader() from surprise module to convert dataframe into surprise dataformat
reader = Reader()

# using the reader to read the trainset
data_2 = Dataset.load_from_df(new_df,reader)
dataset = data_2.build_full_trainset()

print('Number of users: ', dataset.n_users, '\n')
print('Number of Restaurants: ', dataset.n_items)

# Set seed for reproducibility
np.random.seed(42)
# Initialize model with random_state
svd = SVD(random_state=42)
# Run cross-validation with a single processing thread to ensure consistent results
results = cross_validate(svd, data_2, cv=5, n_jobs=1)
# Print results
for values in results.items():
    print(values)
print("-------------------------")
print("Mean RMSE: ", results['test_rmse'].mean())
print("Mean MAE: ", results['test_mae'].mean())

# Set seed
np.random.seed(42)
# Define a dictionary params with hyperparameter values to be tested
param_grid = {'n_factors': [20, 50, 100], # number of factors for matrix factorization
         'reg_all': [0.02, 0.05, 0.1] , 'random_state': [42]} # regularization term
# create a GridSearchCV object 'g_s_svd' for hyperparameter tuning
g_s_svd = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=5, n_jobs=-1)
# Fit the GridSearchCV object to the data to find the best hyperparameters
g_s_svd.fit(data_2)
# Print results
print(g_s_svd.best_score)
print(g_s_svd.best_params)
# created an instance of the SVD model with specified hyperparameters
svd = SVD(n_factors= 20, reg_all=0.02)
# fit the SVD model to the dataset
svd=svd.fit(dataset)

# saved model to reuse
modelname = "svdmodel.zip"
pickle.dump(svd, open(modelname, 'wb'))
print("oke dồi nhé")