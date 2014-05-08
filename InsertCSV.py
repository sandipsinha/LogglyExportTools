import MySQLdb

db=MySQLdb.connect(host="chopperuirds.cd51aabgcrxz.us-west-2.rds.amazonaws.com",user="jasonsk", passwd="sKKl24McZFzN",db="dev", local_infile = 1)

sql = """load data local infile '/home/ubuntu/DataSync/converted.csv'
into table loggly
FIELDS TERMINATED BY ','
lines TERMINATED BY '\n'
IGNORE 1 LINES;"""

cursor = db.cursor()
r = cursor.execute(sql)
db.commit()
db.close()

if(r > 0):
  print "loaded " + str(r) + " rows"
else:
  print "error"
