LogglyExportTools
=================

Export events from Loggly and into various other systems.  The tools are designed to be chained together.  For example, to load events from Loggly into MySQL, first run DownloadJSON, then json2csv, the LoadCSVIntoSQL.  You can setup a cron to do this every day.

**DownloadJSON** - Downloads one day worth of data from Loggly matching your query. You can download up to 5000 events at a time. It stores the data as JSON.
>usage: DownloadJSON.py [-h] username password subdomain query outputFile

**json2csv** - Converts a JSON file into a CSV file. The outline file maps from the json keys to column names. Read more at https://github.com/evidens/json2csv
>usage: json2csv.py [-h] [-e] [-o OUTPUT_CSV] json_file key_map

**LoadCSVIntoSQL** - Inserts a CSV file into the given database table. Make sure the columns in your CSV file match the columns in the database first.
>usage: LoadCSVIntoSQL.py [-h] username password host database table inputFile

**ImportJSONToMixpanel** - Import from a Loggly JSON file into Mixpanel
>usage: ImportJSONToMixpanel.py [-h] inputFile
