#!/bin/bash

rm -rf lambda_package
rm -f ingestion_lambda.zip

mkdir lambda_package

pip install \
  psycopg2-binary \
  python-dotenv \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target lambda_package

cp -r src lambda_package/

cd lambda_package
zip -r ../ingestion_lambda.zip .
cd ..

echo "Lambda zip created: ingestion_lambda.zip"