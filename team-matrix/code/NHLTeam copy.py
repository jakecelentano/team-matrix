import requests
from NHLPlayer import NHLPlayer
from NHLGame import NHLGame
from config import STATS_API_PREFIX, DEFAULT_HEADERS
import datetime
import cairosvg
import os
import json
import time

class NHLTeam(object):
    def __init__(self, team_id, team_name, team_abbreviation, team_link):
        self.team_id = team_id
        self.team_name = team_name
        self.team_abbreviation = team_abbreviation
        self.team_link = STATS_API_PREFIX + team_link
        self.headers =  DEFAULT_HEADERS

    def __str__(self):
        return self.team_name

    def __repr__(self):
        return self.team_name

    def getId(self):
        return self.team_id


    def getRoster(self):
        roster = []
        retries = 0

        while not roster and retries < 5:
            try:
                roster_json = requests.get(url=self.team_link + '/roster', headers=self.headers).json()
                for player in roster_json['roster']:
                    roster.append(NHLPlayer(player['person']['id'], player['person']['fullName'], player['person']['link']))
            except:
                print("Couldn't get roster for {}".format(self.team_name))
                retries += 1
                time.sleep(10)

        return roster

    def player_by_name(self, name):
        for player in self.get_roster():
            if player.player_name == name:
                return player

    def get_schedule(self, start_date, end_date):
        games = []
        retries = 0
        while not games and retries < 5:
            try:
                schedule_json = requests.get(url='https://statsapi.web.nhl.com/api/v1/schedule?startDate={}&endDate={}&teamId={}'.format(start_date, end_date, self.team_id), headers=self.headers).json()
                for date in schedule_json['dates']:
                    for game in date['games']:
                        games.append(NHLGame(game['gamePk'], game['link']))
            except:
                print("Couldn't get schedule for {}".format(self.team_name))
                retries += 1
                time.sleep(10)
        return games

    def get_next_games(self, num_games=2):
        days = 14
        start_date = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        games = self.get_schedule(start_date, end_date)
        num = len(games)
        while num < num_games:
            days += 14
            end_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            games = self.get_schedule(start_date, end_date)
            num = len(games)
        return games[:num_games]
    

    def get_logo(self):
        # check if logo already exists
        
        if os.path.isfile('logos/{}.png'.format(self.team_name)):
            return 'logos/{}.png'.format(self.team_name)
        else:
            url = LOGO_API_PREFIX + '/{}.svg'.format(self.team_id)
            try:
                cairosvg.svg2png(url=url, write_to='logos/{}.png'.format(self.team_name), output_width=100, output_height=100)
            except:
                print("Couldn't get logo for {}".format(self.team_name))
                print(url)
                return 'logos/{}.png'.format('nhl')
                

        return 'logos/{}.png'.format(self.team_name)
    
    
    def get_team_json(self):
        json = None
        retries = 0
        while not json and retries < 5:
            try:
                json = requests.get(url='https://statsapi.web.nhl.com/api/v1/teams/{}'.format(self.team_id), headers=self.headers).json()
            except:
                print("Couldn't get team json for {}".format(self.team_name))
                retries += 1
                time.sleep(10)
        return json
    
    def get_team_stats_json(self):
        json = None
        retries = 0
        while not json and retries < 5:
            try:
                json = requests.get(url='https://statsapi.web.nhl.com/api/v1/teams/{}/stats'.format(self.team_id), headers=self.headers).json()
            except:
                print("Couldn't get team stats json for {}".format(self.team_name))
                retries += 1
                time.sleep(10)
        return json

    def get_wins(self):
        return self.get_team_stats_json()['stats'][0]['splits'][0]['stat']['wins']
    
    def get_losses(self):
        return self.get_team_stats_json()['stats'][0]['splits'][0]['stat']['losses']

    def get_ot(self):
        return self.get_team_stats_json()['stats'][0]['splits'][0]['stat']['ot']
    
    
    def get_team_colors(self):
        json_file = open('nhl_colors.json', 'r')
        json_data = json.load(json_file)
        
        for team in json_data:
            if team['name'] == self.team_name:
                colors = team['colors']['hex']
                colors = [self.hexToRGB(color) for color in colors]
                return colors
        

        return [self.hexToRGB('#123456'), self.hexToRGB('#FFFFFF')]
    

    def get_name(self):
        return self.team_name
    
    def get_abbreviation(self):
        return self.team_abbreviation
    
    def get_record(self):
        json_file = open('nhl_standings.json', 'r')
        json_data = json.load(json_file)
        
        for team in json_data['records']:
            if team['team']['name'] == self.team_name:
                return team['leagueRecord']['wins'], team['leagueRecord']['losses'], team['leagueRecord']['ot']
        
        return 0, 0, 0
    


    
    def hexToRGB(self, hex):
        hex = hex.lstrip('#')
        hlen = len(hex)
        return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))
    
    def get_primary_color(self):
        colors = self.get_team_colors()
        for color in colors:
            r = color[0]
            g = color[1]
            b = color[2]
            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if (luma > 40):
                return color
        return (255, 255, 255)
                





        


        
