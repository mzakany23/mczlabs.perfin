def bucket_munger(aggregations):
    buckets = []
    for query_name, query_body in aggregations.items():
        _item = {
            'query_name' : query_name,
            'query_items' : []
        }
        for k, v in query_body.items():
            _item['query_items'] = [{'key' : k, 'value' : v } for k, v in query_body.items()]
        buckets.append(_item)
    return buckets


def get_query_body(account, equality, date_range):
    account = account.upper()

    return "account:{} AND amount: {} AND date:[{}]".format(
        account,
        equality,
        date_range
    )


def average(query_name, query_body):
    return {
        "query" : {
          "query_string": {
            "query": query_body
          }
        },
        "size" : 0,
        "aggs" : {
            query_name : {
              "avg" : {
                "field" : "amount"
              }
            }
        }
    }


def extended_stats(query_name, query_body):
    return {
        "query" : {
          "query_string": {
            "query": query_body
          }
        },
        "size" : 0,
        "aggs" : {
            query_name : {"extended_stats" : {"field" : "amount"}}
        }
    }


def top_x_transactions_per_period(query_name, query_body):
    return {
      "size": 0,
      "query": {
        "query_string": {
            "query": query_body
        }
      },
      "aggs": {
        query_name : {
          "date_histogram": {
            "field": "date",
            "interval": "week"
          },
          "aggs": {
            "top_keywords": {
              "terms": {
                "field": "group",
                "size": 10
              }
            }
          }
        }
      }
    }
