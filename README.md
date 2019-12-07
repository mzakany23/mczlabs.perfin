# Perfin Ingestion
Read financial CSV files, encode and upload transactions to elasticsearch.

### Running tests

```
pytest -p no:warnings
pytest --cov ./lib -p no:warnings
```

### Dependencies
 - elasticsearch
 - aws lambda
 - python 3.7
 - sentry