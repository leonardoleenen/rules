# -*- coding: UTF-8 -*-
'''
:Authors
	- Enzo D. Grosso
'''

from flask import current_app
from utils import repo
from time import time
from datetime import datetime


def initDerog():

	today_date = datetime.fromtimestamp(time()).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

	client = repo.get_instance({'instance': 'rulz'})

	objs = client.get_by_query('instruments', {})

	if objs is None or len(objs) == 0:
		return

	for obj in objs:
		ending_date = ''

		if 'ending_date' in obj and (type(obj['ending_date']) is str or type(obj['ending_date']) is unicode):
			ending_date = obj['ending_date']

		current_app.logger.debug(ending_date)
		if ending_date == today_date:
			derogate(obj)


def derogate(instrument):
    print instrument
