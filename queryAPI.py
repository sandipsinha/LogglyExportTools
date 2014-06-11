__author__ = 'Mauricio Roman'

""" This module contains functions for generic querying of Loggly API
    The code for initiating the search and fetching the results was forked from
    https://github.com/mostlyjason/LogglyExportTools

    This API has functions to grab more than 5000 results from the Loggly API
"""

import json, csv, time, pytz
import re, math, sys
import requests                                 # For REST API
import urllib2, simplejson                      # For logging with Loggly
from numpy import *
import datetime

def initiateSearch(subdomain, query, searchFrom, searchTo, username, password):
    """ Initiates the search, and returns a temporary ID """

    # We request results in pages of 500 events
    # We search in ascending order, so as to build a constantly growing timeline
    search_url = ("https://" + subdomain + ".loggly.com/apiv2/search?q=" + query + "&from=" +
                   str(searchFrom) + "&until=" + str(searchTo) + "&order=asc&size=500")

    print "Search URL: " + search_url

    # We launch the search
    r = requests.get(search_url, auth=(username, password), timeout=60)

    try:
        rsid = r.json()['rsid']['id']
	print "rsid: " + str(rsid)

    except ValueError:
        print "Error obtaining data"
        return -1

    return rsid


def fetchResults(subdomain, rsid, username, password, newFile, formatFunc, jsonFlag):
    """ Collects the results from a search that was initialized, one page at a time, and returns the entire list
        As one of its inputs, it requires a formatting function, located in the queryFormat module
    """

    #We loop through all the pages, each of which has 500 events, up to max_events

    page = 0
    d = []
    max_events = 5000
    total_events = 1
    page_size = 500
    events_loaded = 0

    while(page * page_size < min(total_events, max_events)):

        results_url = "http://" + subdomain + ".loggly.com/apiv2/events"
        url_params = {'rsid':str(rsid),'page':str(page)}

        retries = 0
        resp1 = ""
        resp2 = ""

        while(retries < 5):
            r = requests.get(results_url, params=url_params, auth=(username, password), timeout=300)

            try:

                #resp1 is the raw json tree, which includes info on total events
                resp1 = r.json()

                #resp2 is a table with the features we want
                try:
                    resp2 = formatFunc(resp1)
                except KeyError:
                    raise ValueError('invalid input for format function')
                #print resp2

                newFile = 0
                break

            except ValueError:
                print "Error status code: " + str(r.status_code) + " msg: " + r.text
                retries = retries + 1
        # End Inner While Loop

        if(retries == 5):
            print "Too many retries, giving up"
            break

        # If this is the first page...
        if not d:
            total_events = resp1['total_events']
            # If total_events exceeds return capacity, break and return
            
	    if jsonFlag:
	    	d = {}
	    	d['events'] = []
	    if total_events > max_events:
                break

        if jsonFlag:
	    for e in resp2['events']:
		d['events'].append(e)
            # Upper bound on events loaded...
            events_loaded = len(d['events'])
        else:
            for e in resp2:
                d.append(e)
            # Exact number of events loaded
            events_loaded = len(d)

        page = page + 1

    total = [total_events, events_loaded]

    return (total, d)


def getSearch(query, formatFunc, searchFrom_init, searchToFinal, step,
              outputFile, newFile, jsonFlag,
              subdomain, username, password, loggly_key = None):
    """ Collects search results in several steps, adjusting the time step dynamically """

    session_id = int(round(time.time() * 1000))

    # If our flag indicates a new file, open for writing, else append to existing file
    if newFile:
        f = open(outputFile, 'w')
    else:
        f = open(outputFile, 'a')

    # If writing to CSV, open file as CSV
    if not jsonFlag:
        wr = csv.writer(f)

    i = 0

    delta_step = []
    searchFrom = []
    searchTo = []
    total_events = []
    events_loaded = []

    delta_step.append(step)             # Step in seconds
    searchFrom.append(searchFrom_init)
    searchTo.append(searchFrom[0] + datetime.timedelta(0,delta_step[0]))

    print "step, total events, events loaded"

    while searchTo[i] <= searchToFinal:

    	rsid = initiateSearch(subdomain, query, searchFrom[i], searchTo[i],
                              username, password)

        if rsid > 0:
            newFile = 0
            ([x1, x2], data) = fetchResults(subdomain, rsid, username, password, newFile, formatFunc, jsonFlag)

            total_events.append(x1)
            events_loaded.append(x2)

            # Print to console for control of process
            print str(i) + "," + str(total_events[i]) + "," + str(events_loaded[i])

            # We only write to file if the total events returned is less than the limit
            write_flag = (total_events[i] <= events_loaded[i])

            # We log the query results, before changing the search from and to parameters
            if loggly_key is not None:
 	    	logQuery(loggly_key, session_id, searchFrom[i], searchTo[i], events_loaded[i], total_events[i], write_flag, i)

            # Calculate the time step dynamically based on previous data
            delta_step.append(getTimeStep(searchFrom, searchTo, total_events, write_flag, i))

            # Write only if we get all the records that we asked for, as there is no guarantee that, if we receive
            # a subset of all records, that they will start at the SearchFrom time
            if(write_flag):
		if jsonFlag:
		    f.write(json.dumps(data))
		else:
                    for item in data:
                        wr.writerow(item)

                searchFrom.append(searchTo[i])
            else:
                searchFrom.append(searchFrom[i])

            #endif
            searchTo.append(searchFrom[i+1] + datetime.timedelta(0,delta_step[i+1]))

        else:
            print "Could not initiate search...exiting"
            break

        time.sleep(3)   # Pause a few seconds so that we do not overwhelm Loggly servers
        i += 1

    return delta_step.pop()

    f.closed


def getTimeStep(searchFrom, searchTo, total_events, write_flag, count):
    """ Calculates time step...taking the latest history into account
        The API returns 5000 records maximum, and there is no guarantee that
        these will be time aligned with the initial time requested. For simplicity,
        we prefer to only accept returns that are below 5000 records """

    max_events = 5000
    vel = []

    # Calculate average "speed" using the last 30 records

    for i in range(count+1)[-30:]:
        diff = searchTo[i] - searchFrom[i]
        delta_sec = diff.total_seconds()
        vel.append(total_events[i] / delta_sec)

    vel = array(vel)
    avg = average(vel)
    std_dev = std(vel)

    #If we failed in our previous estimation, use the point velocity measure plus one std. dev.
    if not write_flag:
        delta_sec = max_events / (vel[-1:] + std_dev)

    #Otherwise, let us just use the average plus one std. dev.
    else:
        delta_sec = max_events / (avg + std_dev)

    return asscalar(delta_sec)


def logQuery(loggly_key, session_id, searchFrom, searchTo, events_loaded, total_events, write_flag, count):
    """ Sends a log to Loggly reporting the status of the search """
    log_data = "PLAINTEXT=" + urllib2.quote(simplejson.dumps(
                  {
                  'timestamp':str(datetime.datetime.today()) , 'level':'info', 'session_id':session_id,
                  'from':str(searchFrom), 'until':str(searchTo),
                  'events_loaded':events_loaded, 'total_events':total_events, 'write_flag':write_flag, 'count':count
                   }))
    # Send log data to Loggly
    urllib2.urlopen("https://logs-01.loggly.com/inputs/" + loggly_key + "/tag/queryAPI/", log_data)


def getUTCtime(timezone, t0, t1, dst0, dst1):
    """ Transforms time from 'timezone' to UTC """
    local = pytz.timezone (timezone)
    t0 = local.localize(t0, is_dst=dst0).astimezone(pytz.utc)
    t1   = local.localize(t1,   is_dst=dst1).astimezone(pytz.utc)
    return t0, t1
