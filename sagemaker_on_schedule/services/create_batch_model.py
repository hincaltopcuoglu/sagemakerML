import tarfile

import boto3
from sagemaker.serverless import ServerlessInferenceConfig
from sagemaker.sklearn.model import SKLearnModel

TARGET_BUCKET = '' #write your target bucket here


s3 = boto3.client("s3")

with tarfile.open("model.tar.gz", "w:gz") as myzip:
    myzip.add("model.joblib")

s3.upload_file("model.tar.gz", TARGET_BUCKET, "model.tar.gz")

model = SKLearnModel(
    model_data="s3://{}/test/model.tar.gz".format(TARGET_BUCKET),
    role="AmazonSageMaker-ExecutionRole-20230117T102682",
    entry_point="upload.py",
    framework_version="1.0-1",
)

serverless_config = ServerlessInferenceConfig()

serverless_predictor = model.deploy(serverless_inference_config=serverless_config)
