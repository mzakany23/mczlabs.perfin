import logging

from perfin.util.dynamodb_conn import get_user_accounts
# from perfin.util.es.es_conn import search
# from perfin.util.email.ses_conn import send_email

logger = logging.getLogger(__file__)

'''
	DESCRIPTION
		PERFIN_ENV=local python query.py
		PERFIN_ENV=base python query.py

		# defaults to base
		python query.py
'''

if __name__ == '__main__':
	'''
		ideas:
		1. periodic automated ingest
		probably want to store these results weekly in s3
		but don't need the dependency of printing a file
		so we should ingest new transactions daily
		but we should ingest csv files weekly
		todo: turn off ingest lambda
		goal: two periodic tasks
		1. one ingest daily function
		2. one ingest csv file weekly function

		periodic task that will run everyday or every couple of days
		that will print a csv and upload it to s3
		then will ingest the docs
		then will add a log in dynamo db indicating
		what the filename was and what the date was and account_id

		2. periodic automated summary email
		periodic task tha does some summary stats and sends an email on saturdays
		tells you how much you have in all your accounts
		tells you top transactions
		tells you unusual transactions

		3. logging
		make sure that good exception info is reported to sentry

		todo
		work on elasticsearch queries to
		try and see if can get good info
	'''

	# res = search('stats', 'chase', '>0', '2020-01-01 TO *')
	# print(res)
	# print('ok')


	# for k, v in res['aggregations'].items():
		# import pdb; pdb.set_trace()

	# Replace sender@example.com with your "From" address.
	# This address must be verified with Amazon SES.

	# date_range = '2020-01-01 TO *'
	# equality = '<0'
	# account = 'chase'
	# send_email(date_range, equality, account)
	# PerfinUploadLog.create_table(wait=True)
	# log = PerfinUploadLog(
	# 	filename='somefilename.txt',
	#     from_date='2020-01-01',
	#     to_date='*',
	#     account_name='chase',
	# )

	# log.save()

	# for account in get_user_accounts('mzakany', 'chase'):
	# 	import pdb; pdb.set_trace()

	logger.debug('this is  a log message')
