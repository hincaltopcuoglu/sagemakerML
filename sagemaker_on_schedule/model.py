import os
import sys
import warnings
from datetime import timedelta

import joblib
import pandas as pd
import psycopg2

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

warnings.filterwarnings("ignore")

# Connection parameters, yours will be different
param_dic = {
    "host": DB_HOST,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
}


def connect(params_dic):
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn


conn = connect(param_dic)
df_price = pd.read_sql('select * from "Daily_Prices"', con=conn)


def preprocessing(df):
    df.drop("wsj", axis=1, inplace=True)

    df["odate"] = pd.to_datetime(df["odate"], format="%Y%m%d").dt.strftime("%Y%m%d")

    df_last = df.sort_values(by="odate", ascending=True)

    df_last["rate"] = df_last["sales"] / df_last["leads"]

    df_last["Target"] = df_last["price"].shift(-1)

    df_fpred = df_last[["odate", "price", "leads", "sales", "Target"]]

    return df_fpred


def train_test(df):
    df_fpred = preprocessing(df)

    train = df_fpred[
        (
            pd.to_datetime(df_fpred["odate"])
            <= (pd.to_datetime(df_fpred["odate"].max()) - timedelta(days=61))
        )
    ]

    test = df_fpred[
        (
            pd.to_datetime(df_fpred["odate"])
            > (pd.to_datetime(df_fpred["odate"].max()) - timedelta(days=61))
        )
        & (
            (
                pd.to_datetime(df_fpred["odate"])
                <= (pd.to_datetime(df_fpred["odate"].max()) - timedelta(days=1))
            )
        )
    ]

    pred = df_fpred[
        pd.to_datetime(df_fpred["odate"])
        > (pd.to_datetime(df_fpred["odate"].max()) - timedelta(days=1))
    ]

    return train, test, pred


def model(df):
    train, test, pred = train_test(df)

    features = ["price", "leads", "sales"]

    model = RandomForestRegressor(n_estimators=5, random_state=0)

    X_train = train[features]
    y_train = train["Target"]

    X_test = test[features]
    y_test = test["Target"]

    X_pred = pred[features]
    y_pred = pred["Target"]  # TODO: CHECK IT THIS IS CORRECT - WE DONT USE!!!

    model.fit(X_train, y_train)
    model_path = os.path.join(".", "model.joblib")
    joblib.dump(model, model_path)
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)

    # TODO: CHECK IT THIS IS CORRECT - WE DONT USE!!!
    r2_score_train = r2_score(y_train, pred_train)
    r2_score_test = r2_score(y_test, pred_test)
    mse_test = mean_squared_error(y_test, pred_test)

    prediction = model.predict(X_pred)

    return prediction