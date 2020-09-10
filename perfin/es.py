import logging
import threading

import certifi
from elasticsearch import Elasticsearch
from perfin.settings import config

local = threading.local()
logger = logging.getLogger(__name__)

DOC_TYPE = config.ES_DOC_TYPE
INDEX = config.ES_INDEX
SCHEMA = config.ES_SCHEMA


def get_es():
    def _conn():
        es_node = config.ES_NODE
        es_user = config.ES_USER
        es_pass = config.ES_PASS

        if es_user and es_pass:
            logger.debug("using non local elasticsearch:{}".format(es_node))
            params = {
                "http_auth": (es_user, es_pass),
                "send_get_body_as": "POST",
                "ca_certs": certifi.where(),
                "use_ssl": True,
                "send_get_body_as": "POST",
            }
            return Elasticsearch([es_node], **params)

        return Elasticsearch([config.ES_NODE])

    try:
        es = local.es
    except AttributeError:
        es = _conn()
        local.es = es
    return es


def create_index():
    es = get_es()

    if not es.indices.exists(INDEX):
        return es.indices.create(index=INDEX, body=SCHEMA)


def insert_document(document, **kwargs):
    es = get_es()
    unique_doc_id = config.generate_specific_key(*document.values())
    return es.index(
        index=INDEX,
        doc_type=DOC_TYPE,
        body=document,
        id=unique_doc_id,
        request_timeout=60,
    )
