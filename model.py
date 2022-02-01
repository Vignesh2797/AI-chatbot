import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression  
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
import sklearn.metrics as metrics
from sklearn.metrics import mean_squared_error


def get_data(a):
    data_path = "./static/assets/configuration/WEYMTH_WATRLMN_OD_a51_2018_1_1.csv"
    data = pd.read_csv(data_path, low_memory=False)



    data = data[["tpl", "pta", "ptd", "arr_at", "dep_at"]]
    data.dropna(subset=["pta"], inplace=True)
    data = data.replace(to_replace=":", value=".", regex=True)
    cleaned_data = data.copy()
    cleaned_data.drop(["tpl"], axis=1, inplace=True)
    cleaned_data = cleaned_data.astype(float)
    cleaned_data = cleaned_data.fillna(0)
    new_data = cleaned_data.copy()
    target = new_data.arr_at
    new_data.drop("arr_at", axis=1, inplace=True)

    train_X, test_X, train_y, test_y = train_test_split(new_data, target, test_size=0.2)


    #Linear Regression
    # lr= LinearRegression()  
    # lr.fit(train_X, train_y)  
    # pred_lr = lr.predict(test_X)  
    # print('Train Score: ', lr.score(train_X, train_y))  
    # print('Test Score: ', lr.score(test_X, test_y))  
    # print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_lr), 2))
    # print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_lr), 2))
    # print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y,pred_lr)))

    #Lasso Regression
    # lasso = Lasso(alpha=1.0)
    # lasso.fit(train_X, train_y)
    # pred_lasso = lasso.predict(test_X)
    # print('Train Score: ', lasso.score(train_X, train_y))  
    # print('Test Score: ', lasso.score(test_X, test_y))  
    # print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_lasso), 2))
    # print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_lasso), 2))
    # print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y,pred_lasso)))

    #Ridge Regression
    # ridge = Ridge(alpha=1.0)
    # ridge.fit(train_X, train_y)
    # pred_ridge = ridge.predict(test_X)
    # print('Train Score: ', ridge.score(train_X, train_y))  
    # print('Test Score: ', ridge.score(test_X, test_y)) 
    # print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_ridge), 2))
    # print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_ridge), 2))
    # print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y, pred_ridge))) 

    #Decision Tree Regression
    # clf_tree=DecisionTreeRegressor(random_state=0)
    # clf_tree.fit(train_X,train_y)
    # pred_clf = clf_tree.predict(test_X)
    # print('Train Score: ', clf_tree.score(train_X, train_y))  
    # print('Test Score: ', clf_tree.score(test_X, test_y))  
    # print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_clf), 2))
    # print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_clf), 2))
    # print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y, pred_clf)))

    #KNN Regression
    # knn = KNeighborsRegressor()
    # knn.fit(train_X, train_y)
    # pred_knn = knn.predict(test_X)
    # print('Train Score: ', knn.score(train_X, train_y))  
    # print('Test Score: ', knn.score(test_X, test_y))  
    # print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_knn), 2))
    # print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_knn), 2))
    # print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y, pred_knn)))



    clf_rf = RandomForestRegressor(random_state=0)
    clf_rf.fit(train_X, train_y)
    pred_clf = clf_rf.predict(test_X)
    print('Train Score: ', clf_rf.score(train_X, train_y))  
    print('Test Score: ', clf_rf.score(test_X, test_y))  
    print("Mean squared error: " , np.round(metrics.mean_squared_error(test_y, pred_clf), 2))
    print("Mean absolute error: ", np.round(metrics.mean_absolute_error(test_y, pred_clf), 2))
    print('Root Mean Square Error:',np.sqrt(mean_squared_error(test_y, pred_clf)))

    data_path = "./static/assets/configuration/WEYMTH_WATRLMN_OD_a51_2018_10_10.csv"
    data = pd.read_csv(data_path, low_memory=False)
    data = data[["tpl", "pta", "ptd", "arr_at", "dep_at"]]
    data.dropna(subset=["pta"], inplace=True)
    data = data.replace(to_replace=":", value=".", regex=True)
    cleaned_data = data.copy()
    cleaned_data.drop(["tpl"], axis=1, inplace=True)
    cleaned_data = cleaned_data.astype(float)
    cleaned_data = cleaned_data.fillna(0)
    cleaned_data.drop("arr_at", axis=1, inplace=True)
    pred = clf_rf.predict(cleaned_data)
    cleaned_data["tpl"] = data["tpl"]
    cleaned_data["arr_at"] = pred
    cleaned_data["delay"] = cleaned_data["arr_at"] - cleaned_data["pta"]

    val = cleaned_data.loc[cleaned_data["tpl"] == a["currentStation"]]
    mean_val = val["delay"].mean()
    delay = int(a["predictDelay"]) + mean_val
    delay = int(delay)
    return delay


