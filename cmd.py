import argparse
import parser
import os
import shutil
import time
import zipfile

# get date
p = argparse.ArgumentParser()
p.add_argument("date", help="Format is mmddyyyy")
args = p.parse_args()
c = parser.Controller()
date_obj = time.strptime(args.date, "%m%d%Y")

# convert to espn format
date = time.strftime("%Y%m%d", date_obj)

# generate files
(dir, zip) = c.generate_playbyplay_csv(date)

#unzip the file and remove the directory, and then the zip file
zipf = zipfile.ZipFile(zip)
shutil.rmtree(dir)
zipf.extractall()
os.remove(zip)

