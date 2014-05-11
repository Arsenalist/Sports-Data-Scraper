import io
import os
import zipfile
from bs4 import BeautifulSoup
import time
import requests
import re
import sys
import uuid
import shutil
import time

class PlayByPlayParser:
    def __init__(self, game_id):
        self.PBP_BASE_URL = "http://scores.espn.go.com/nba/playbyplay?period=0"
        self.game_id = game_id
        self.html = self.get_html()
        s = BeautifulSoup(self.html, "html5lib")

    def get_html(self):
        return requests.get(self.PBP_BASE_URL + "&gameId=" + self.game_id).text

    def get_home_team(self):
        s = BeautifulSoup(self.html, "html5lib")
        table = s.find('table', attrs={'class': 'mod-data'})
        return table.thead.contents[1].contents[3].string;
       

    def to_csv(self):   
        s = BeautifulSoup(self.html)
        table = s.find('table', attrs={'class': 'mod-data'})
        pbp = ""
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            row_text = ''
            for td in tds:
                cell_text = td.findAll(text=True)[0].replace(u'\xa0', ' ').strip()
                if cell_text != '':
                    row_text = row_text + cell_text + ","
            row_text = row_text.rstrip(",")
            if row_text != '':
                pbp = pbp + row_text + "\n"
        return pbp.rstrip("\n")

class ScoreboardParser:
    def __init__(self, date):
        self.BASE_URL = 'http://scores.espn.go.com/nba/scoreboard?date='
        self.date = date

    def get_html(self):
        return requests.get(self.BASE_URL + self.date).text

    def get_game_ids(self):
        html = self.get_html()
        soup = BeautifulSoup(html, "html5lib")
        game_ids = []
        tags = soup.findAll(attrs={'id': re.compile(r".*statusLine1")})
        for tag in tags:
            game_ids.append(tag['id'].split('-')[0])

        return game_ids
 

class Controller:
    def generate_playbyplay_csv(self, date):
        prnit "in the controller"
        sys.stdout.flush()
        s = ScoreboardParser(date)
        game_ids = s.get_game_ids()
        dir_name = str(uuid.uuid4())
        dir_path = "./" + dir_name + "/"
        os.makedirs(dir_path)

        date_obj = time.strptime(date, "%Y%m%d")   
        date_for_user = time.strftime("%m%d%Y", date_obj)

        for game_id in game_ids:
            print "doing this now "
            sys.stdout.flush()
            print "Current Game: " + game_id
            p = PlayByPlayParser(game_id)
            print "Parsed Play By Play"
            csv_path = dir_path + p.get_home_team().title().replace(" ", "_") + "_" + date_for_user + ".csv"
            self.write_to_file(csv_path, p.to_csv())
            print "File Created"
        
        zip_path = "./playbyplay_" + date_for_user + "_" + dir_name + ".zip"
        print "About to create zip..."
        self.create_zip(zip_path, dir_path, "playbyplay_" + date_for_user)
        print "Zip created....." + zip_path
        shutil.rmtree(dir_path)
        return zip_path

    def playbyplay_handler(self, date, email):
        zip_file = self.generate_playbyplay_csv(date)
        self.send_playbyplay_email("Play by Play for " + date_for_user, email, zip_file)
        os.remove(zip_file)

    def send_playbyplay_email(self, subject, to_email, file):
        print "Sending email to " + to_email + " with attachment " + file
        r = requests.post("https://api.mailgun.net/v2/arsenalist.com/messages",
                            auth=("api", "key-87e4l1772aqgc5prnavmr1ecm9iqgr43"),
                            files=[("attachment", open(file))],
                            data={"from": "Arsenalist Mailer <mailer@arsenalist.com>",
                                  "to": to_email,
                                  "subject": subject,
                                  "text": "A zip file is attached."})   
        if r.status_code != 200:
            print r.text


    def write_to_file(self, absolute_path, content):
        f = open(absolute_path,'w+')
        f.write(content.encode('utf-8'))
        f.close()

    def read_bytes(self, file_path):
        in_file = open(file_path, "rb")
        data = in_file.read()
        in_file.close()   
        return data

    def create_zip(self, zip_path, dir_path, parent):
        zipf = zipfile.ZipFile(zip_path, 'w')
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                name = os.path.join(root, file)
                zipf.write(name, parent + "/" + file)
        zipf.close()
        return zipf


    def convert_to_bytes(self, dir_path, zip_path):
        zip_bytes = self.read_bytes(zip_path)
        return zip_bytes



