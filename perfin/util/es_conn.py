import logging

import certifi

from elasticsearch import Elasticsearch

from perfin.util.s3_conn import get_s3_processed_docs

from .globals import ES_NODE, ES_PASS, ES_USER, INDEX

logger = logging.getLogger(__file__)

perfin_schema = {
    "settings": {
        "number_of_shards": 2,
        "max_result_window": 1000000
    },
    "aliases" : {
        "{}_read".format(INDEX) : {},
        "{}_write".format(INDEX) : {},
    },
    "mappings": {
        "default": {
            "dynamic": "true",
            "properties": {
                "account": {"type": "keyword"},
                "name": {"type": "keyword"},
                "date": {"type": "date"},
                "description": {"type": "text", "fielddata" : True},
                "amount": {"type": "float"},
                "group" : {"type": "keyword"}
            }
        }
    }
}


def get_es_connection(**kwargs):
    if ES_USER and ES_PASS:
        params = {
            "http_auth" : (ES_USER, ES_PASS),
            "send_get_body_as" : "POST",
            "ca_certs" : certifi.where(),
            "use_ssl" : True,
            "send_get_body_as" : "POST"
        }
        return Elasticsearch([ES_NODE], **params)
    else:
        logger.info('using test elasticsearch')
        return Elasticsearch(['http://localhost:9200'])

    return None


def create_index(es, index_name, schema):
    return es.indices.create(
        index=index_name,
        body=schema)


def delete_index(es, index_name):
    return es.indices.delete(index=[index_name])


def insert_document(es, index, unique_doc_id, document, **kwargs):
    doc_type = kwargs.get("doc_type", "default")

    return es.index(
        index=index,
        doc_type=doc_type,
        body=document,
        id=unique_doc_id,
        request_timeout=60)


def create_perfin_index():
    es = get_es_connection()
    return create_index(es, INDEX, perfin_schema)


def insert_all_rows(filter_key=None):
    bucket = 'mzakany-perfin'
    path = '{}/original_archive'.format(bucket)
    es = get_es_connection()
    for row in get_s3_processed_docs(path, filter_key=filter_key):
        document = row["document"]
        document["group"] = row["_group"]
        write_alias = '{}_write'.format(INDEX)
        insert_document(es, write_alias, row["_id"], document)
