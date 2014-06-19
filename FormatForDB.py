import datetime, re, urllib

# scrub special chars  so conversion to CSV works correctly
def scrubSpecialChars(e):
  if((type(e) == type(str())) | (type(e) == type(unicode()))):
    if((type(e) == type(str())) & ('%' in str(e))):
    	e = urllib.unquote(e).decode('utf-8')
    return re.sub('[,"\'\n\r\t\\\\]', ' ', e)
  elif(type(e) == type(dict())):
    for k, v in e.items():
      e[k] = scrubSpecialChars(v)
    return e
  elif(type(e) == type(list())):
    for i in range(len(e)):
	e[i] = scrubSpecialChars(e[i])
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
    e['events'][i] = scrubSpecialChars(en)
  return e
