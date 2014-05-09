import base64, argparse, requests, json, time, datetime

parser = argparse.ArgumentParser()
parser.add_argument("inputFile")
args = parser.parse_args()

json_data=open(args.inputFile)

events = json.load(json_data)
json_data.close()
mpevents = []

for i in range(0, len(events['events'])):
  try: 
    e = events['events'][i]
    eventName = e['event']['json']['ui']['label']
    t = e['timestamp'].encode("ascii")
    t = time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple())
    host = e['event']['json']['location']['host']
    path = e['event']['json']['location']['pathname']
  except KeyError:
    continue
  
  mp = {}
  mp['event'] = eventName
  mp['properties'] = {}
  mp['properties']['distinct_id'] = host
  mp['properties']['time'] = t
  mp['properties']['path'] = path
  mp['properties']['token'] = 'd30fc9eeac0d785681e9f3790a549cb7'
  mpevents.append(mp)

key = 'c8aa7e545dbbe6e5c95e046b8e3a6305'

for e in mpevents:
  data = base64.b64encode(json.dumps(e))
  import_url = "http://api.mixpanel.com/import/?data=" + data + "&api_key=" + key
  #print import_url
  r = requests.post(import_url)
  print r
