import sys, requests, json, datetime, argparse

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("subdomain")
parser.add_argument("query")
parser.add_argument("outputFile")
args = parser.parse_args()

# truncate field values to 128 characters so they fit in varchar columns
def truncate(e):
  if((type(e) == type(str())) | (type(e) == type(unicode()))):
    return e[0:127]
  elif(type(e) == type(dict())):
    for k, v in e.items():
      e[k] = truncate(v)
    return e

# convert loggly timestamp to mysql format
def convertTimestamp(t):
  milliseconds = int(str(t)[-3:])
  unix_timestamp = int(str(t)[0:-3])
  the_date = datetime.datetime.fromtimestamp(unix_timestamp)
  the_date += datetime.timedelta(milliseconds=milliseconds)
  return the_date.strftime('%Y-%m-%d %H:%M:%S.%f')

# reformate loggly events for mysql
def formatForDB(e):
  for i in range(0, len(e['events'])):
    en = e['events'][i]
    en['timestamp'] = convertTimestamp(en['timestamp'])
    e['events'][i] = truncate(en)
  return e


yesterday = datetime.date.today() - datetime.timedelta(days=1)
dayBefore = datetime.date.today() - datetime.timedelta(days=2)

search_url = "http://" + args.subdomain + ".loggly.com/apiv2/search?q=" + args.query + "&from=" + str(dayBefore) + "T00%3A00%3A00.000Z&until=" + str(yesterday) + "T00%3A00%3A00.000Z&size=500"

print "Search string: " + search_url

r = requests.get(search_url, auth=(args.username, args.password))
rsid = r.json()['rsid']['id']

total_events = 1
page = 0
data = ""

while(page * 500 < total_events):
  results_url = "http://" + args.subdomain + ".loggly.com/apiv2/events?rsid=" + str(rsid) + "&page=" + str(page)
  
  retries = 0
  resp = ""

  while(retries < 5):
    r = requests.get(results_url, auth=(args.username, args.password))
    try:
      resp = formatForDB(r.json())
      break
    except ValueError:
      print "Error status code: " + str(r.status_code) + " msg: " + r.text
      retries = retries + 1

  if(retries == 5):
    print "Too many retries, giving up"
    break

  if not data:
    data = resp
    total_events = resp['total_events']
    print "Total results: " + str(total_events)
  else:
    for e in resp['events']:
      data['events'].append(e) 
  
  page = page + 1
  print "Events loaded: " + str(len(data['events']))

f = open(args.outputFile,'w') 
f.write(json.dumps(data))
f.close()
