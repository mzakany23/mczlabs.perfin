import json

import logging

import certifi

from elasticsearch import Elasticsearch

from perfin.settings.base import load_settings
from perfin.util.s3_conn import get_s3_processed_docs

from .queries import (
    average,
    extended_stats,
    get_query_body,
    top_x_transactions_per_period
)


logger = logging.getLogger(__name__)


def get_schema(index):
    return  {
        "settings": {
            "number_of_shards": 2,
            "max_result_window": 1000000
        },
        "aliases" : {
            "{}_read".format(index) : {},
            "{}_write".format(index) : {},
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


def get_es_config():
    '''
        DESCRIPTION
        es_node, es_user, es_pass, index = (
            settings['ES_NODE'],
            settings['ES_USER'],
            settings['ES_PASS'],
            settings['INDEX']
        )
    '''
    settings = load_settings()
    return (
        settings['ES_NODE'],
        settings['ES_USER'],
        settings['ES_PASS'],
        settings['INDEX']
    )


def get_es_connection(**kwargs):
    es_node, es_user, es_pass, index_name = get_es_config()

    if es_user and es_pass:
        logger.debug('using non local elasticsearch:{}'.format(es_node))
        params = {
            "http_auth" : (es_user, es_pass),
            "send_get_body_as" : "POST",
            "ca_certs" : certifi.where(),
            "use_ssl" : True,
            "send_get_body_as" : "POST"
        }
        return Elasticsearch([es_node], **params)
    else:
        logger.debug('using test elasticsearch')
        return Elasticsearch(['http://localhost:9200'])

    return None


def create_index(*args):
    if len(args) == 3:
        es, index_name, schema = args
    else:
        es_node, es_user, es_pass, index_name = get_es_config()
        es = get_es_connection()
        schema = get_schema(index_name)

    if es.indices.exists(index_name):
        logger.info('host {} and index {} exists!'.format(es_node, index_name))
        return
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


def create_perfin_index(es, index):
    return create_index(es, index, get_schema())


def insert_all_rows(index, filter_key=None):
    bucket = 'mzakany-perfin'
    path = '{}/original_archive'.format(bucket)
    es = get_es_connection()
    logger.info('uploading {}'.format(path))
    for row in get_s3_processed_docs(path, filter_key=filter_key):
        logger.info(row)
        document = row["document"]
        document["group"] = row["_group"]
        write_alias = '{}_write'.format(index)
        insert_document(es, write_alias, row["_id"], document)


def search(query_name, account, equality, date_range):
    es_node, es_user, es_pass, index = get_es_config()
    es = get_es_connection()
    average, extended_stats, top_x_transactions_per_period
    lookup = {
        'average' : average,
        'stats' : extended_stats,
        'top_transactions' : top_x_transactions_per_period
    }
    fn = lookup[query_name]
    query_body = get_query_body(account, equality, date_range)
    body = fn(query_name, query_body)
    logger.info({
        'query_name' : query_name,
        'index' : index,
        'query' : json.dumps(body)
    })
    res = es.search(index, body=body)
    total = res['hits']['total']
    hits = res['hits']['hits']
    return {
        'hits' : hits,
        'total' : total,
        'aggregations' : res['aggregations']
    }
