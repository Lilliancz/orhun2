from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
from otree.api import Submission
import random as r

class PlayerBot(Bot):

    def play_round(self):
        score = r.randint(0,5)
        att = score + r.randint(0,5)
        if self.player.id_in_group == 1:
            yield (pages.ChooseFirm, {'firm': 'A', 'time_ChooseFirm': 'test', 'switch': 'No', 'q6': 'test'})
        yield (pages.Instructions1, {'time_Instructions1': 'test'})
        yield Submission(pages.Game1, 
            {'time_Game1': 'test', 'game1_score': score, 'attempted': att},
            check_html=False)
        yield (pages.Results1, {'time_Results1': 'test'})
