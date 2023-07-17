import sys
from ast import literal_eval

import boto3
import pandas as pd
import psycopg2

param_dic = {
    "host"      : "us-east-1.rds.amazonaws.com",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "--"
}

def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn

smaker_run = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):

    # STEP 1: CONNECT TO THE DATABASE
    conn = connect(param_dic)

    df_price = pd.read_sql('select * from "Daily_Prices"', con=conn)
    #print(df_slo)
    
    # STEP 2: QUERY DB FOR LATEST INPUT DATA
    pred = df_price[pd.to_datetime(df_price['odate']) == (pd.to_datetime(df_slo['odate'].max()))]
    
    features = ['price','leads','sales']
    pred = pred[features]
    # STEP 3: TURN THE INPUT DATA INTO A CSV BYTE STRING (this is a sample)
    data_in = pred.to_csv(header=False,index=False).strip('\n').encode('utf-8')

    print(data_in)
    #data_in = b'1.6812,25.0,4.192200557103064,1.0222841225626742,1392.0,3.877437325905293,36.06,-119.01\n2.5313,30.0,5.039383561643835,1.1934931506849316,1565.0,2.679794520547945,35.14,-119.46'


    # STEP 4: PASS DATA TO SAGEMAKER 

    resp = smaker_run.invoke_endpoint(
        EndpointName='sagemaker-scikit-learn-2023-02-10-16-39-57-581',
        Body=data_in,
        ContentType='text/csv')['Body'].read().decode(encoding='utf-8')

    result = literal_eval(resp)

    # STEP 5: SAVE DATA IN RESULT (an array) TO DATABASE

    print('Input Data: {}'.format(str(data_in)))
    print('Prediction: ' + str(result))
   #res = {"Prediction": result}
   #return json.dumps(res)


#lambda_handler(None,None)
