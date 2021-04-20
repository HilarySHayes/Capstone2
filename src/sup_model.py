import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV

def prepare_data(df):
    X = df.drop("mode", axis=1).values
    y = df['mode'].copy().values
    return train_test_split(X, y)

def search_for_model(X_train, y_train, random_grid, n_iter, cv):
    clf = RandomForestClassifier()
    clf_random = RandomizedSearchCV(estimator=clf, 
                               param_distributions=random_grid, 
                               n_iter=n_iter, 
                               cv=cv, 
                               n_jobs=-1)
    clf_random.fit(X_train, y_train)
    return clf_random.best_estimator_

def confusion_plot(X_test, y_test, clf):
    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
    _, ax = plt.subplots(figsize=(8,8))
    disp.plot(xticks_rotation=90, ax=ax)
    plt.show()

if __name__ == '__main__':
    df = pd.read_parquet("../data/featurized.parquet")
    X_train, X_test, y_train, y_test = prepare_data(df)
    clf = RandomForestClassifier(bootstrap=False, max_depth=15, max_features='sqrt',
                      min_samples_split=5, n_estimators=600)
    clf.fit(X_train, y_train)
    confusion_plot(X_test, y_test, clf)
    # with open('../data/model.pkl', 'wb') as f:
    #     pickle.dump(clf, f)

    # random_grid = {'bootstrap': [True, False],
    #          'max_depth': [4, 6, 8, 10, 15, 20, 30],
    #          'max_features': ['auto', 'sqrt'],
    #          'min_samples_leaf': [1, 2, 4, 6],
    #          'min_samples_split': [2, 5, 10, 15],
    #          'n_estimators': [100, 200, 400, 600]}
    # print(search_for_model(X_train, y_train, random_grid, 10, 3))