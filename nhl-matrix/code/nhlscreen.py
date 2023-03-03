#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time
from nhl import NHL
from team import Team
import datetime
from config import DEFAULT_TEAM
from PIL import Image



class NHLScreen(SampleBase):
    def __init__(self, *args, **kwargs):
        super(NHLScreen, self).__init__(*args, **kwargs)
        self.color = graphics.Color(255, 255, 255)
        self.team = None
        self.nhl = NHL(str(datetime.datetime.now().year))

    # main function
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        nhl = NHL(str(datetime.datetime.now().year))
        self.team = nhl.get_team_by_name(DEFAULT_TEAM)
        team_primary_color = self.team.get_primary_color()
        self.color = graphics.Color(team_primary_color[0], team_primary_color[1], team_primary_color[2])


        offscreen_canvas = self.getUpcomingGamesScreen()
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        while True:
            time.sleep(10)
            # wait for keyboard interrupt
            try:
                pass
            except KeyboardInterrupt:
                print("Keyboard interrupt")
                break

    
    def drawBorder(self, offscreen_canvas=None):
        color = self.color
        if offscreen_canvas is None:
            offscreen_canvas = self.matrix.CreateFrameCanvas()
        graphics.DrawLine(offscreen_canvas, 0, 0, 63, 0, color)
        graphics.DrawLine(offscreen_canvas, 0, 0, 0, 63, color)
        graphics.DrawLine(offscreen_canvas, 63, 0, 63, 63, color)
        graphics.DrawLine(offscreen_canvas, 0, 63, 63, 63, color)
        #offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    def getUpcomingGameScreen(self):
        color = self.color
        team = self.team
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.drawBorder(offscreen_canvas)
        font = graphics.Font()
        font.LoadFont("fonts/4x6.bdf")
        
        game = team.get_next_games(1)[0]
        x, y = 2, 2
        home_team = self.nhl.get_team_by_id(game.get_game_home_team_id())
        away_team = self.nhl.get_team_by_id(game.get_game_away_team_id())
        # get logo paths
        home_team_logo = home_team.get_logo()
        away_team_logo = away_team.get_logo()
        # convert to 30x30 PIL images in RGB
        home_team_logo = Image.open(home_team_logo)
        home_team_logo.thumbnail((30, 30), Image.ANTIALIAS)
        home_team_logo = home_team_logo.convert('RGB')
        away_team_logo = Image.open(away_team_logo)
        away_team_logo.thumbnail((30, 30), Image.ANTIALIAS)
        away_team_logo = away_team_logo.convert('RGB')
        # paste logos onto canvas
        offscreen_canvas.SetImage(home_team_logo, x, y)
        offscreen_canvas.SetImage(away_team_logo, x+30, y)

        # draw vs between logos
        graphics.DrawText(offscreen_canvas, font, x+15, y+30, color, "vs")

        game_time = game.get_game_time()
        graphics.DrawText(offscreen_canvas, font, x, y+30, color, game_time)
        graphics.DrawText(offscreen_canvas, font, x, y+30, color, game_time)
        y += 30
        
        return offscreen_canvas
        
        





# Main function
if __name__ == "__main__":
    screen = NHLScreen()
    if (not screen.process()):
        screen.print_help()
