# Perfin Ingestion
Read financial CSV files, encode and upload transactions to elasticsearch. Checkout config/base.json and serverless.yaml to see how env vars are set. 

### Running tests

```
#main
pytest -p no:warnings

#coverage
pytest --cov=./lib -p no:warnings

#integration
ES_NODE=http://localhost:9200 RUN_INTEGRATION_TESTS=1 pytest -p no:warnings
```

### Dependencies
 - elasticsearch [6.5.2](https://www.elastic.co/downloads/past-releases/elasticsearch-6-5-2)
 - aws lambda
 - python 3.7+
 - sentry (optional)
 - [serverless](https://serverless.com/)

## Setup Cluster Locally
Make sure you have elastisearch running locally (http://localhost:9200)
```
#create index with default schema
ES_NODE=http://localhost:9200  python -c "exec(\"from util.es import create_perfin_index\ncreate_perfin_index()\")"

#insert some docs
ES_NODE=http://localhost:9200 RUN_INTEGRATION_TESTS=1 pytest -p no:warnings
```
### Deploying 
Service uses [serverless](https://serverless.com/) to deploy lambda

```
serverless deploy
```