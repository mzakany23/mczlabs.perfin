# Perfin Ingestion
Read financial CSV files, encode and upload transactions to elasticsearch.

### Running tests

```
pytest
pytest --cov=./lib
```

### Dependencies
 - elasticsearch
 - aws lambda
 - python 3.7
 - sentry