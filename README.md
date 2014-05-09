LogglyExportTools
=================

Export events from Loggly and into various other systems

**DownloadJSON** - Downloads one day worth of data from Loggly matching your query. You can download up to 5000 events at a time. It stores the data as JSON.
>usage: DownloadJSON.py [-h] username password subdomain query outputFile

**json2csv** - Converts a JSON file into a CSV file. The outline file maps from the json keys to column names.
>usage: json2csv.py [-h] [-e] [-o OUTPUT_CSV] json_file key_map

**LoadCSVIntoSQL** - Inserts a CSV file into the given database table
>usage: LoadCSVIntoSQL.py [-h] username password host database table inputFile

**ImportJSONToMixpanel** - Import from a Loggly JSON file into Mixpanel
>usage: ImportJSONToMixpanel.py [-h] inputFile
