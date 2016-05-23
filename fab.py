# -*- coding: utf-8 -*-
import requests, json, phabricator, datetime
from prettyprint import pp as ppr
import settings
apiToken = settings.API_TOKEN

fab = phabricator.Phabricator(
	host = settings.API_ENTRY, 
	token = apiToken, 
	)

transactions = fab.maniphest.gettasktransactions(ids=["1"]).response
ppr(transactions)
quit()

firstTask =  fab.maniphest.query(ids=[1]).response.values()[0]
createDate = datetime.datetime.fromtimestamp(int(firstTask["dateCreated"]))
print createDate

quit()
resp = requests.post("http://192.168.0.121:8100/api/conduit.getcertificate", data = {"api.token": "api-3o74h37rwikuran7gc7fjvvnwivl"})
print resp.text
resp = requests.post("http://192.168.0.121:8100/api/user.whoami", data = {"api.token": "api-3o74h37rwikuran7gc7fjvvnwivl"})
print resp.text

