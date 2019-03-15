import os
from elasticsearch import helpers
from .perfin import local_print_out

try:
    from private_env import *
    pass
except:
    raise Exception("private_env does not exist!")
        
def test_process():    

    print("------------------------------------------") 
    print("local testing")
    print("------------------------------------------") 
    print("ES_NODE:%s" % os.environ.get("ES_NODE"))
    print("ES_USER:%s" % os.environ.get("ES_USER"))
    print("ES_PASS:%s" % os.environ.get("ES_PASS"))
    print("------------------------------------------") 

    event = {
      'Records': [
        {
          's3': {
            's3SchemaVersion': '1.0',
            'configurationId': '07cdd4c6-53ea-41d1-9536-e64d6661708d',
            'bucket': {
              'name': 'mzakany-perfin',
              'ownerIdentity': {
                'principalId': 'A1KXLJ5C0RVBLI'
              },
              'arn': 'arn:aws:s3:::mzakany-perfin'
            },
            'object': {
              # 'key': 'CAPONE_VENTURE_20180217.csv',
              # 'key' : '2018-10-10_transaction_download_2.csv',
              'key' : '2018-10-10_transaction_download_5.csv',
              # 'key': 'EXPORT.CSV',
              # 'key': 'CHASE_SAPH_20180114.CSV',
              'size': 2577,
              'eTag': '47eb72587b90a88cf07820543e938d11',
              'sequencer': '005BB006BB55D4F51F'
            }
          }
        }
      ]
    }
    
    # es = get_es_connection()

    # query = {
    #     "query_string" : {
    #         "query" : "account:CAPITAL_ONE"
    #     }
    # }

    # results = helpers.scan(es,
    #     query={"query": query},
    #     index="perfin_read",
    #     doc_type="default"
    # )

    # for result in results:
    #     print(result)
    #     import pdb; pdb.set_trace()

    # create_perfin_index()
    # lambda_insertion_into_es(event, "context")
    local_print_out(event, "context")
    # local_insertion_all_s3_csvs_into_es()
