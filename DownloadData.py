import sys, requests, json, datetime

def truncate(e):
  if((type(e) == type(str())) | (type(e) == type(unicode()))):
    return e[0:127]
  elif(type(e) == type(dict())):
    for k, v in e.items():
      e[k] = truncate(v)
    return e

def convertTimestamp(t):
  milliseconds = int(str(t)[-3:])
  unix_timestamp = int(str(t)[0:-3])
  the_date = datetime.datetime.fromtimestamp(unix_timestamp)
  the_date += datetime.timedelta(milliseconds=milliseconds)
  return the_date.strftime('%Y-%m-%d %H:%M:%S.%f')

def formatForDB(e):
  for i in range(0, len(e['events'])):
    en = e['events'][i]
    en['timestamp'] = convertTimestamp(en['timestamp'])
    e['events'][i] = truncate(en)
  return e

#search_url = "http://chopperui.loggly.com/apiv2/search?q=*&from=2014-04-28T00%3A00%3A00.000Z&until=2014-04-29T00%3A00%3A00.000Z&size=500"

yesterday = datetime.date.today() - datetime.timedelta(days=1)
dayBefore = datetime.date.today() - datetime.timedelta(days=2)

search_url = "http://chopperui.loggly.com/apiv2/search?q=json.ui.label%3Averify&from=" + str(dayBefore) + "T00%3A00%3A00.000Z&until=" + str(yesterday) + "T00%3A00%3A00.000Z&size=500"

print "searching for: " + search_url

r = requests.get(search_url, auth=('jasons', 'ivy8Bona'))
rsid = r.json()['rsid']['id']

total_events = 1
page = 0
data = ""

while(page * 500 < total_events):
  results_url = "http://chopperui.loggly.com/apiv2/events?rsid=" + str(rsid) + "&page=" + str(page)
  
  retries = 0
  resp = ""

  while(retries < 10):
    r = requests.get(results_url, auth=('jasons', 'ivy8Bona'))
    try:
      resp = formatForDB(r.json())
      break
    except ValueError:
      print "Error status code: " + str(r.status_code) + " msg: " + r.text
      retries = retries + 1

  if(retries == 10):
    print "Too many retries, giving up"
    break

  if not data:
    data = resp
    total_events = resp['total_events']
    print "total events: " + str(total_events)
  else:
    for e in resp['events']:
      data['events'].append(e) 
  
  page = page + 1
  print "events: " + str(len(data['events']))

f = open('chopperui.json','w') 
f.write(json.dumps(data))
f.close()
