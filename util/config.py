from functools import reduce
from .support import strip_white


FIFTH_THIRD_LOOKUP = {
    "EAST OHIO GAS PAYMENT" : {
        "name" : "PAYMENT_UTILITY_GAS",
        "category" : "UTILITY",
        "organization" : "EAST_OHIO",
        "expense_type" : "FIXED"
    },
    "WEB INITIATED PAYMENT AT CHASE CREDIT" : {
        "name" : "PAYMENT_CHASE_CC",
        "category" : "CREDIT_CARD_PAYMENT",
        "organization" : "CHASE_BANK",
        "expense_type" : "VARIABLE"
    },
    "FIRST NATL BANK" : {
        "name" : "FAIRFAX_MORTGAGE",
        "category" : "MORTGAGE",
        "organization" : "FIRST_NATIONAL_BANK",
        "expense_type" : "FIXED"  
    },
    "ELECTRONIC IMAGE" : {
        "name" : "CHECK",
        "category" : "FINANCIAL",
        "organization" : "FIFTH_THIRD_BANK",
        "expense_type" : "VARIABLE"    
    },
    "5/3 ID ALERT" : {
        "name" : "IDENTITY_ALERT",
        "category" : "INSURANCE",
        "organization" : "FIFTH_THIRD_BANK",
        "expense_type" : "FIXED"      
    },
    "JEANIE WITHDRAWAL" : {
        "name" : "ATM_WITHDRAWAL",
        "category" : "BANKS",
        "organization" : "BANKS",
        "expense_type" : "VARIABLE"        
    },
    "LMCU MORTGAGE PAYMENT" : {
        "name" : "SHAKER_RD_MORTGAGE",
        "category" : "BANKS",
        "organization" : "LAKE_MICHEGAN_CREDIT_UNION",
        "expense_type" : "FIXED"        
    },
    "KENT STATE UNIVE PAYROLL" : {
        "name" : "KENT_STATE_INCOME",
        "category" : "WORK",
        "organization" : "KENT_STATE",
        "expense_type" : "INCOME"        
    },
    "VERTICAL K DIR DEP" : {
        "name" : "VK_INCOME",
        "category" : "WORK",
        "organization" : "VERTICAL_KNOWLEDGE",
        "expense_type" : "INCOME"        
    },
    "WEB INITIATED PAYMENT AT CWD" : {
        "name" : "CWD",
        "category" : "MISC",
        "organization" : "CWD",
        "expense_type" : "VARIABLE"        
    },
    "NAVIENT NAVI DEBIT" : {
        "name" : "NAVIENT_STUDENT_LOANS",
        "category" : "BANKS",
        "organization" : "LAKE_MICHEGAN_CREDIT_UNION",
        "expense_type" : "FIXED"        
    },
    "MUSICAL ARTS ASS PAYROLL" : {
        "name" : "TCO_INCOME",
        "category" : "PAYCHECK",
        "organization" : "THE_CLEVELAND_ORCHESTRA",
        "expense_type" : "INCOME"        
    }

}

OTHER_LOOKUP = {
    "ML_CLASSIFIED" : {
        "category" : "ML_CLASSIFIED",
        "expense_type" : "ML_CLASSIFIED"
    }
}

CHASE_LOOKUP = {
    "CLEVELAND CINEMAS" : {
        "name" : "CLEVELAND_CINEMAS",
        "category" : "MOVIES",
        "organization" : "CLEVELAND_CINEMAS",
        "expense_type" : "VARIABLE"        
    },
    "COOLBEANZ BA" : {
        "name" : "COOLBEANZ_CAFE",
        "category" : "COFFEE",
        "organization" : "COOLBEANZ_CAFE",
        "expense_type" : "VARIABLE"        
    },
    "MARSHALLS" : {
        "name" : "MARSHALLS",
        "category" : "CLOTHES",
        "organization" : "MARSHALLS",
        "expense_type" : "VARIABLE"        
    },
    "BP" : {
        "name" : "BP",
        "category" : "GAS",
        "organization" : "BP",
        "expense_type" : "VARIABLE"        
    },
    "NANCY L RUBEL PHD" : {
        "name" : "JO_THEREPY",
        "category" : "THEREPY",
        "organization" : "NANCY_RUBEL",
        "expense_type" : "VARIABLE"        
    },
    "STARBUCKS" : {
        "name" : "STARBUCKS",
        "category" : "COFFEE",
        "organization" : "STARBUCKS",
        "expense_type" : "VARIABLE"
    },
    "HOLY FAMILY RETREAT CENTE" : {
        "name" : "HOLY_FAMILY_RETREAT",
        "category" : "YOGA_RETREAT",
        "organization" : "HOLY_FAMILY_RETREAT_CENTER",
        "expense_type" : "VARIABLE"
    },
    "SHELL OIL" : {
        "name" : "SHELL_GAS",
        "category" : "GAS",
        "organization" : "SHELL_OIL",
        "expense_type" : "VARIABLE"
    },
    "POTBELLY" : {
        "name" : "POTBELLY",
        "category" : "RESTARAUNT",
        "organization" : "POTBELLY",
        "expense_type" : "VARIABLE"
    },
    "PANERA BREAD" : {
        "name" : "PANERA",
        "category" : "RESTARAUNT",
        "organization" : "PANERA",
        "expense_type" : "VARIABLE"
    },
    "CVS/PHARMACY" : {
        "name" : "CVS",
        "category" : "MISC",
        "organization" : "CVS_PHARMACY",
        "expense_type" : "VARIABLE"
    },
    "CLEVELAND WATER INTERNET" : {
        "name" : "CLEVELAND_WATER_BILL",
        "category" : "PAYMENT_UTILITY_WATER",
        "organization" : "CLEVELAND_WATER_BILL",
        "expense_type" : "VARIABLE"
    },
    "WHOLEFDS CTR" : {
        "name" : "WHOLE_FOODS",
        "category" : "GROCERY_STORE",
        "organization" : "WHOLE_FOODS",
        "expense_type" : "VARIABLE"
    },
    "SUNOCO" : {
        "name" : "SUNOCO",
        "category" : "GAS",
        "organization" : "SUNOCO",
        "expense_type" : "VARIABLE"
    },
    "HIGH THAI" : {
        "name" : "HIGH_THAI",
        "category" : "RESTARAUNT",
        "organization" : "HIGH_THAI",
        "expense_type" : "VARIABLE"
    },
    "NEORSD INTERNET PAYMENTS" : {
        "name" : "NEO_SEWER_BILL",
        "category" : "PAYMENT_UTILITY_SEWER",
        "organization" : "NORTH_EAST_OHIO_SEWER",
        "expense_type" : "VARIABLE"
    },
    "NC SOCCER SHOP" : {
        "name" : "NC_HUDSON_SOCCER_SHOP",
        "category" : "CLOTHES",
        "organization" : "NC_SOCCER_HUDSON",
        "expense_type" : "VARIABLE"
    },
    "LYFT" : {
        "name" : "LYFT_TAXI",
        "category" : "TRANSPORTATION",
        "organization" : "LYFT",
        "expense_type" : "VARIABLE"
    },
    "SPIRIT AIRL" : {
        "name" : "SPIRIT_AIRLINES",
        "category" : "AIR_TRAVEL",
        "organization" : "SPIRIT_AIRLINES",
        "expense_type" : "VARIABLE"
    },
    "THE UPS STORE" : {
        "name" : "UPS_STORE",
        "category" : "MISC",
        "organization" : "STARBUCKS",
        "expense_type" : "VARIABLE"
    },
    "ALL MATTERS GALLERY" : {
        "name" : "ALL_MATTERS_GALLARY",
        "category" : "MISC",
        "organization" : "ALL_MATTERS_GALLARY",
        "expense_type" : "VARIABLE"
    },
    "VENMO" : {
        "name" : "VENMO_PAY_APP",
        "category" : "FINANCIAL",
        "organization" : "VENMO",
        "expense_type" : "VARIABLE"
    },
    "COVENTRY INN" : {
        "name" : "INN_ON_COVENTRY",
        "category" : "RESTARAUNT",
        "organization" : "STARBUCKS",
        "expense_type" : "VARIABLE"
    },
    "HEIGHTS ANIMAL HOSPITAL" : {
        "name" : "HEIGHTS_ANIMAL_HOSPITAL",
        "category" : "VETINARY",
        "organization" : "HEIGHTS_ANIMAL_HOSPITAL",
        "expense_type" : "VARIABLE"
    },
    "OLIVE GARDEN" : {
        "name" : "OLIVE_GARDEN",
        "category" : "RESTARAUNT",
        "organization" : "STARBUCKS",
        "expense_type" : "VARIABLE"
    },
    "TARGET" : {
        "name" : "TARGET",
        "category" : "MISC",
        "organization" : "TARGET",
        "expense_type" : "VARIABLE"
    },
    "BEST BUY" : {
        "name" : "BEST_BUY",
        "category" : "ELECTRONICS",
        "organization" : "BEST_BUY",
        "expense_type" : "VARIABLE"
    },
    "WALGREENS" : {
        "name" : "WALGREENS",
        "category" : "MISC",
        "organization" : "WALGREENS",
        "expense_type" : "VARIABLE"
    },
    "GOOGLE" : {
        "name" : "GOOGLE",
        "category" : "MISC",
        "organization" : "GOOGLE",
        "expense_type" : "VARIABLE"
    },
    "AIRBNB" : {
        "name" : "AIRBNB",
        "category" : "HOTELS",
        "organization" : "AIRBNB",
        "expense_type" : "VARIABLE"
    },
    "ALADDINS EATERY" : {
        "name" : "ALADDINS",
        "category" : "RESTARAUNT",
        "organization" : "ALADDINS",
        "expense_type" : "VARIABLE"
    },
    "LUSH BEACHWOOD" : {
        "name" : "LUSH_BOTIQUE",
        "category" : "MAKEUP",
        "organization" : "LUSH",
        "expense_type" : "VARIABLE"
    },
    "DAVE'S SUPERMARKET" : {
        "name" : "DAVES_MARKET",
        "category" : "GROCERY_STORE",
        "organization" : "DAVES_MARKET",
        "expense_type" : "VARIABLE"
    },
    "YOGA ROOTS" : {
        "name" : "YOGA_ROOTS",
        "category" : "YOGA",
        "organization" : "YOGA_ROOTS",
        "expense_type" : "VARIABLE"
    },
    "COSTCO WHSE" : {
        "name" : "COSTCO",
        "category" : "GROCERY_STORE",
        "organization" : "COSTCO",
        "expense_type" : "VARIABLE"
    },
    "TOMMYS" : {
        "name" : "TOMMYS",
        "category" : "RESTARAUNT",
        "organization" : "TOMMYS",
        "expense_type" : "VARIABLE"
    },
    "Payment Thank You" : {
        "name" : "PAYMENT_RECEIVED_CHASE_CC",
        "category" : "PAYMENT",
        "organization" : "PAYMENT_RECEIVED_CHASE_CC",
        "expense_type" : "VARIABLE"
    },
    "CLEV HTS - PARKING" : {
        "name" : "CLEVELAND_HEIGHTS_PARKING",
        "category" : "PARKING",
        "organization" : "CLEVELAND_HEIGHTS_PARKING",
        "expense_type" : "VARIABLE"
    },
    "MARATHON" : {
        "name" : "MARATHON",
        "category" : "GAS",
        "organization" : "MARATHON",
        "expense_type" : "VARIABLE"
    },
    "STONE OVEN" : {
        "name" : "STONE_OVEN",
        "category" : "RESTARAUNT",
        "organization" : "STONE_OVEN",
        "expense_type" : "VARIABLE"
    },
    "JENIS SPLENDID" : {
        "name" : "JENIS_ICECREAM",
        "category" : "RESTARAUNT",
        "organization" : "JENIS_ICECREAM",
        "expense_type" : "VARIABLE"
    },
    "MAROTTA S RESTARAUNT" : {
        "name" : "MAROTTAS",
        "category" : "RESTARAUNT",
        "organization" : "MAROTTAS",
        "expense_type" : "VARIABLE"
    },
    "LUNA BAKERY" : {
        "name" : "LUNAS",
        "category" : "RESTARAUNT",
        "organization" : "LUNAS",
        "expense_type" : "VARIABLE"
    },
    "PHOENIX COFFEE" : {
        "name" : "PHOENIX_COFFEE",
        "category" : "COFFEE",
        "organization" : "PHOENIX_COFFEE",
        "expense_type" : "VARIABLE"
    },
    "FAIRMOUNT MARTINI" : {
        "name" : "THE_FAIRMOUNT",
        "category" : "BARS",
        "organization" : "THE_FAIRMOUNT",
        "expense_type" : "VARIABLE"
    },
    "REGAL RICHMOND TOWN" : {
        "name" : "REGAL_RICHMOND",
        "category" : "MOVIES",
        "organization" : "REGAL_RICHMOND",
        "expense_type" : "VARIABLE"
    },
    "L'ALBATROS" : {
        "name" : "LALBATROS",
        "category" : "RESTARAUNT",
        "organization" : "LALBATROS",
        "expense_type" : "VARIABLE"
    },
    "ARHAUS FURNITURE" : {
        "name" : "ARHAUS",
        "category" : "FURNITURE",
        "organization" : "ARHAUS",
        "expense_type" : "VARIABLE"
    },
    "PETPEOPLE UNIVERSITY" : {
        "name" : "PETPEOPLE",
        "category" : "ANIMAL_CARE",
        "organization" : "LUNAS",
        "expense_type" : "VARIABLE"
    },
    "OTANI NOODLE" : {
        "name" : "OTANI_NOODLE",
        "category" : "RESTARAUNT",
        "organization" : "OTANI_NOODLE",
        "expense_type" : "VARIABLE"
    },
    "SEPHORA" : {
        "name" : "SEPHORA",
        "category" : "MAKEUP",
        "organization" : "SEPHORA",
        "expense_type" : "VARIABLE"
    },
    "HEINENS" : {
        "name" : "HEINENS",
        "category" : "GROCERY_STORE",
        "organization" : "HEINENS",
        "expense_type" : "VARIABLE"
    },
    "ZARA USA" : {
        "name" : "ZARAS",
        "category" : "CLOTHES",
        "organization" : "ZARAS",
        "expense_type" : "VARIABLE"
    },
    "CITY OF KENT PARKING" : {
        "name" : "KENT_STATE_PARKING",
        "category" : "PARKING",
        "organization" : "KENT_STATE",
        "expense_type" : "VARIABLE"
    },
    "HELPING HANDS LAWNCAR" : {
        "name" : "HELPING_HANDS_LAWN_CARE",
        "category" : "LAWNCARE",
        "organization" : "HELPING_HANDS_LAWN_CARE",
        "expense_type" : "VARIABLE"
    },
    "LULULEMON" : {
        "name" : "LULULEMON",
        "category" : "CLOTHES",
        "organization" : "LULULEMON",
        "expense_type" : "VARIABLE"
    },
    "PETSMART" : {
        "name" : "PETSMART",
        "category" : "ANIMAL_CARE",
        "organization" : "PETSMART",
        "expense_type" : "VARIABLE"
    },
    "NORDSTROM RACK" : {
        "name" : "NORDSTROM_RACK",
        "category" : "CLOTHES",
        "organization" : "NORDSTROM_RACK",
        "expense_type" : "VARIABLE"
    },
    "EINSTEIN BROS" : {
        "name" : "EINSTEIN_BAGELS",
        "category" : "RESTARAUNT",
        "organization" : "EINSTEIN_BAGELS",
        "expense_type" : "VARIABLE"
    },
    "YOURS TRULY CHAGRIN" : {
        "name" : "YOUR_TRULY",
        "category" : "RESTARAUNT",
        "organization" : "YOUR_TRULY",
        "expense_type" : "VARIABLE"
    }
}

CAPITAL_ONE_LOOKUP = {
    "HEROKU" : {
        "name" : "HEROKU",
        "category" : "SERVER_BILL",
        "organization" : "HEROKU",
        "expense_type" : "VARIABLE"
    }, 
    "Amazon web services" : {
        "name" : "AWS",
        "category" : "SERVER_BILL",
        "organization" : "AWS",
        "expense_type" : "VARIABLE"
    },
    "ENVATO" : {
        "name" : "ENVATO_ELEMENTS",
        "category" : "SERVER_BILL",
        "organization" : "ENVATO_ELEMENTS",
        "expense_type" : "VARIABLE"
    }
}


def get_account_types():
    from functools import reduce
    
    def _fn(accum, current):
        _key = strip_white(current)
        accum[_key] = ACCOUNT_TYPES[current]
        return accum
    return reduce(_fn, ACCOUNT_TYPES.keys(), {})

transactions = [FIFTH_THIRD_LOOKUP, CHASE_LOOKUP, CAPITAL_ONE_LOOKUP, OTHER_LOOKUP]
TRANSACTION_TYPES = reduce((lambda accum, current: dict(accum, **current)), transactions)


