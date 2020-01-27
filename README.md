
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

Deploy using the cli tool (under serverless tab)

```
perfincli
```

## File Analyzing

File Analyzing dertermines the types of the columns of a file in order to build docs.


```python
for file_path in file_paths:
    logger.info('inserting file_path {}'.format(file_path))
    analyzer = FileAnalyzer(file_path=file_path, trim_field='description')
    for row in analyzer.get_rows():
        document = row["document"]
        document["group"] = row["_group"]
        write_alias = '{}_write'.format(INDEX)
        insert_document(ES_CONN, write_alias, row["_id"], document)

```

```python
from perfin.lib.file_matching.analyzer import FileAnalyzer

filename = 'mzakany-perfin/Chase3507_Activity20190314.CSV'
header = ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount']
analyzer = FileAnalyzer(header=header, filename=filename)

assert analyzer.top_match.domain == 'CHASE'

```

The idea is that a file's type will get decoded from a config file so that it can get properly named. When figuring out what file that it is.
