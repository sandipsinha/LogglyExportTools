import sys, requests, json, datetime, argparse
from queryAPI import getSearch, getUTCtime
from FormatForDB import formatForDB

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("accountFqdn")
parser.add_argument("query")
parser.add_argument("outputFile")
args = parser.parse_args()

untildt = datetime.datetime.today() - datetime.timedelta(days=0)
untildt = untildt.replace(hour=0, minute=0, second=0, microsecond=0)
fromdt = datetime.datetime.today() - datetime.timedelta(days=1)
fromdt = fromdt.replace(hour=0, minute=0, second=0, microsecond=0)
step = 86400

print "From: " + str(fromdt)
print "Until: " + str(untildt)

# Pack arguments for search API call
API_request = (args.query, formatForDB)
API_dates = (fromdt, untildt, step)
API_output  = (args.outputFile, 1, 1)
API_credentials = (args.accountFqdn, args.username, args.password)

# launch search
getSearch(*API_request + API_dates + API_output + API_credentials)
