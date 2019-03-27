TEST_FILE_DIR = '/Users/mzakany/desktop/perfin/tests/files'


BASE_POLICY = [
    # chase
    {
        "key" : "CHASE",
        "header" : ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount'],
        "trim" : {
            "field" : "description",
            "value" : 10
        }, 
        "fields" : {
            "date" : 2,
            "description" : 3,
            "amount" : 4
        }
    },
    {
        "key" : "CHASE",
        "header" : ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount'],
        "trim" : {
            "field" : "description",
            "value" : 10
        }, 
        "fields" : {
            "date" : 1,
            "description" : 2,
            "amount" : 5,
            "category" : 3
        }
    },
    # Fifth third
    {
        "key" : "FIFTH_THIRD",
        "header" : ['Date', 'Description', 'Check Number', 'Amount'],
        "trim" : {
            "field" : "description",
            "value" : 10
        }, 
        "fields" : {
            "date" : 0,
            "description" : 1,
            "check_num" : 2,
            "amount" : 3
        }   
    },
    # Capital one
    {
        "key" : "CAPITAL_ONE",
        "header" : [' Transaction Date', ' Posted Date', ' Card No.', ' Description', ' Category', ' Debit', ' Credit'],
        "trim" : {
            "field" : "description",
            "value" : 10
        }, 
        "fields" : {
            "date" : 1,
            "card" : 2,
            "description" : 3,
            "category" : 4,
            "amount" : 5,
            "credit" : 6,
        }     
    }
]
