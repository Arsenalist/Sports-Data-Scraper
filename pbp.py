import argparse
from sportsdata import sportsparser
import os
import time
import zipfile

# get date
p = argparse.ArgumentParser()
p.add_argument("date", help="Format is mmddyyyy")
args = p.parse_args()
c = sportsparser.Controller()
date_obj = time.strptime(args.date, "%m%d%Y")

# convert to espn format
date = time.strftime("%Y%m%d", date_obj)

# generate files
zip = c.generate_playbyplay_csv(date)

#unzip the file and remove the directory, and then the zip file
zipf = zipfile.ZipFile(zip)
zipf.extractall()
os.remove(zip)

