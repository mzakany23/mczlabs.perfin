"""
.venv/bin/python query.py
.venv/bin/ipython -i query.py
"""

from perfin.models import ESPerfinPG, pg_session

session = pg_session()

res = session.query(ESPerfinPG).filter(ESPerfinPG.amount > 0).count()

print(res)
