import MySQLdb, argparse

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("host")
parser.add_argument("database")
parser.add_argument("table")
parser.add_argument("inputFile")
args = parser.parse_args()

db=MySQLdb.connect(host=args.host, user=args.username, passwd=args.password,db=args.database, local_infile = 1)

sql = """load data local infile '""" + args.inputFile + "\' " + \
"into table " + args.table + " " + \
"""FIELDS TERMINATED BY ','
lines TERMINATED BY '\n'
IGNORE 1 LINES;"""

cursor = db.cursor()
r = cursor.execute(sql)
db.commit()
db.close()

if(r > 0):
  print "Loaded " + str(r) + " rows"
else:
  print "Error: " + str(r)
