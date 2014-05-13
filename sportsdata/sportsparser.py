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
        self.soup = BeautifulSoup(self.html, "html5lib")

    def get_html(self):
        r = requests.get(self.PBP_BASE_URL + "&gameId=" + self.game_id)
        if r.status_code != 200:
            raise Exception("Could not get HTML for " + self.game_id + " " + r.text)
        return r.text

    def is_valid(self):
        return self.soup.find('table', attrs={'class': 'mod-data'}) != None

    def get_home_team(self):
        table = self.soup.find('table', attrs={'class': 'mod-data'})
        return table.thead.contents[1].contents[3].string;
       

    def to_csv(self):           
        table = self.soup.find('table', attrs={'class': 'mod-data'})
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
        self.html = self.get_html()
        self.soup = BeautifulSoup(self.html, "html5lib")

    def get_html(self):
        r = requests.get(self.BASE_URL + self.date)
        if r.status_code != 200:
            raise Exception("Could not get HTML for scoreboard " + self.date + " " + r.text)
        return r.text


    def get_game_ids(self):
        game_ids = []
        tags = self.soup.findAll(attrs={'id': re.compile(r".*statusLine1")})
        for tag in tags:
            game_ids.append(tag['id'].split('-')[0])

        print "Game IDs to consider:"
        print game_ids
        return game_ids
 

class Controller:
    def generate_playbyplay_csv(self, date):
        s = ScoreboardParser(date)
        game_ids = s.get_game_ids()
        dir_name = str(uuid.uuid4())
        dir_path = "./" + dir_name + "/"
        os.makedirs(dir_path)

        date_obj = time.strptime(date, "%Y%m%d")   
        date_for_user = time.strftime("%m%d%Y", date_obj)

        for game_id in game_ids:
            print "Game ID being processed is " + game_id
            p = PlayByPlayParser(game_id)
            if p.is_valid():
                csv_path = dir_path + p.get_home_team().title().replace(" ", "_") + "_" + date_for_user + ".csv"
                self.write_to_file(csv_path, p.to_csv())
                print "Done processing for " + game_id
            else:
                print "Play by Play not available for " + game_id
        
        zip_path = "./playbyplay_" + date_for_user + "_" + dir_name + ".zip"
        self.create_zip(zip_path, dir_path, "playbyplay_" + date_for_user)
        shutil.rmtree(dir_path)
        return zip_path

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



