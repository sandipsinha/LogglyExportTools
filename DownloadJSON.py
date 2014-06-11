import sys, requests, json, datetime, argparse
from queryAPI import getSearch, getUTCtime
from FormatForDB import formatForDB

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("subdomain")
parser.add_argument("query")
parser.add_argument("outputFile")
args = parser.parse_args()

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
dayBefore = datetime.datetime.today() - datetime.timedelta(days=2)
dayBefore = dayBefore.replace(hour=0, minute=0, second=0, microsecond=0)
step = 86400

print yesterday
print dayBefore

# Pack arguments for search API call
API_request = (args.query, formatForDB)
API_dates = (dayBefore, yesterday, step)
API_output  = (args.outputFile, 1, 1)
API_credentials = (args.subdomain, args.username, args.password)

# launch search
getSearch(*API_request + API_dates + API_output + API_credentials)
