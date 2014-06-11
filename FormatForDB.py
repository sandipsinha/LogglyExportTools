import datetime

# truncate field values to 128 characters so they fit in varchar columns
def truncate(e):
  if((type(e) == type(str())) | (type(e) == type(unicode()))):
    return e[0:127]
  elif(type(e) == type(dict())):
    for k, v in e.items():
      e[k] = truncate(v)
    return e
  else:
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
  print e  
  return e
