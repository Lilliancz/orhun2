from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import random
import inflect
from django.conf import settings
from otree_mturk_utils.pages import CustomMturkPage, CustomMturkWaitPage


# MANY Thanks to Philipp Chapkovski for the "Record time taken on waitpage" post - Lillian


# wait page before game 1
class Game1WaitPage(CustomMturkWaitPage):
    group_by_arrival_time = True

    # seconds before they can just get paid
    startwp_timer = settings.SESSION_CONFIGS[0]['startwp_timer']

    # skips to end if no partners show up
    skip_until_the_end_of = 'app'


class WhatHappensNextA(CustomMturkPage):
    form_model = 'player'
    timeout_seconds = settings.SESSION_CONFIGS[0]['timeout_seconds']

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutWhatHappensA = True


class ChooseFirm(CustomMturkPage):
    form_model = 'player'
    form_fields = ['firm', 'time_ChooseFirm']

    timeout_submission = {'firm': 'B'}
    timeout_seconds = settings.SESSION_CONFIGS[0]['timeout_seconds']

    def vars_for_template(self):
        return {
            'pageTimeoutWording': self.session.config.get('pageTimeoutWording')
        }

    def before_next_page(self):
        self.player.firm_in_game = self.player.firm
        self.participant.vars['firm_in_game'] = self.player.firm
        if self.timeout_happened:
            self.player.TimeoutChooseFirm = True


# Ask why player 1 chose Firm
class WhyFirm(CustomMturkPage):
    form_model = 'player'
    timeout_seconds = settings.SESSION_CONFIGS[0]['timeout_seconds']
    form_fields = ['q6']

    def vars_for_template(self):
        return {
            'firm': self.player.firm
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutWhyFirm = True


# wait page for all 3 group members
class Game1FirmWaitPage(CustomMturkWaitPage):
    title_text = "Please wait while other participants are finishing up."
    body_text = "Please wait while other participants are finishing up. You will begin the competition \
    when all three participants have arrived to this page. Please do not leave, the wait should not be long. \
    If you are inactive for a while (not on a wait page), you will be kicked out of the study and not get any bonus."
    group_by_arrival_time = False


# Show firm for game 1
class Game1Firm(CustomMturkPage):
    form_model = 'player'
    form_fields = ['time_Game1Firm']
    timeout_seconds = settings.SESSION_CONFIGS[0]['timeout_seconds']

    def vars_for_template(self):
        # set skip to end as false, since they are starting the game
        self.player.skip_to_end = False

        # get opponents
        you = self.player.id_in_group
        opponent1 = self.group.get_player_by_id(you % 3 + 1)
        opponent2 = self.group.get_player_by_id((you + 1) % 3 + 1)

        # get 3 roles
        p1 = self.group.get_player_by_id(1)
        p2 = self.group.get_player_by_id(2)
        p3 = self.group.get_player_by_id(3)

        # assign same problems and answers for each member of group
        p2.participant.vars['game1_problems']=p1.participant.vars['game1_problems']
        p3.participant.vars['game1_problems']=p1.participant.vars['game1_problems']

        p2.participant.vars['game1_answers']=p1.participant.vars['game1_answers']
        p3.participant.vars['game1_answers']=p1.participant.vars['game1_answers']

        self.player.firm_in_game = self.participant.vars['firm_in_game']

        # set list of answers as string so we can see them in dataset
        self.player.game1_answers = ', '.join(str(x) for x in self.participant.vars['game1_answers'])

        return {
            'problems': self.participant.vars['game1_problems'],
            'answers': self.participant.vars['game1_answers'],
            'firm': self.player.firm,
            'firm_in_game': self.player.firm_in_game,
            'baseline': self.player.participant.vars['baseline_score'],
            'opponent1': opponent1.participant.vars['baseline_score'],
            'opponent2': opponent2.participant.vars['baseline_score']
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutGame1Firm = True
        self.player.get_wait1_firm()


# game 1 task
class Game1(CustomMturkPage):
    form_model = 'player'
    form_fields = ['game1_score', 'attempted', 'time_Game1']
    timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    # variables that will be passed to the html and can be referenced from html or js
    def vars_for_template(self):
        return {
            'problems': self.participant.vars['game1_problems'],
            'answers': self.participant.vars['game1_answers']
        }


class Results1WaitPage(CustomMturkWaitPage):
    group_by_arrival_time = False

# need to use skip_to_end otherwise it will try to calculate group payoffs when they skip to end
    def is_displayed(self):
        return not self.player.skip_to_end

    def after_all_players_arrive(self):
        # sets payoffs for group if did not skip to end
        self.group.set_payoffs()


class SeeScoresChoice(CustomMturkPage):
    form_model = 'player'
    form_fields = ['see_scores_choice']

    # only shown to those who chose B initially
    def is_displayed(self):
        return self.player.firm == "B"


# game 1 results
class Results1(CustomMturkPage):
    form_model = 'player'
    form_fields = ['time_Results1']
    # timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    # variables that will be passed to the html and can be referenced from html or js


    def vars_for_template(self):
        # set skip to end as false, since they are starting the game
        self.player.skip_to_end = False

        # get opponents
        you = self.player.id_in_group
        opponent1 = self.group.get_player_by_id(you % 3 + 1)
        opponent2 = self.group.get_player_by_id((you + 1) % 3 + 1)

        # get 3 roles
        p1 = self.group.get_player_by_id(1)
        p2 = self.group.get_player_by_id(2)
        p3 = self.group.get_player_by_id(3)

        # assign same problems and answers for each member of group
        p2.participant.vars['game1_problems']=p1.participant.vars['game1_problems']
        p3.participant.vars['game1_problems']=p1.participant.vars['game1_problems']

        p2.participant.vars['game1_answers']=p1.participant.vars['game1_answers']
        p3.participant.vars['game1_answers']=p1.participant.vars['game1_answers']

        self.player.firm_in_game = self.participant.vars['firm_in_game']

        # set list of answers as string so we can see them in dataset
        self.player.game1_answers = ', '.join(str(x) for x in self.participant.vars['game1_answers'])

        return {
            'answers': self.player.game1_answers,
            'firm': self.player.firm,
            'firm_in_game': self.player.firm_in_game,
            'baseline': self.player.participant.vars['baseline_score'],
            'opponent1': opponent1.participant.vars['baseline_score'],
            'opponent2': opponent2.participant.vars['baseline_score'],
            'attempted': self.player.attempted,
            'correct': self.player.game1_score,
            'see_scores_choice': self.player.see_scores_choice,

            # automatically pluralizes the word 'problem' if necessary
            'problems': inflect.engine().plural('problem', self.player.attempted)
        }

    def before_next_page(self):
        self.player.get_wait1_results()
        self.player.payoff = self.player.game1_bonus
        print(self.player.payoff)
        if self.timeout_happened:
            self.player.TimeoutResults1 = True


class FinalSurvey(CustomMturkPage):
    form_model = 'player'
    form_fields =['time_FinalSurvey', 'q8', 'q10','q11','q12']
    # timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutFinalSurvey = True


class FinalSurveyA(CustomMturkPage):
    form_model = 'player'
    form_fields = ['q7_choice', 'q7']
    # timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    def vars_for_template(self):
        firm = self.player.firm_in_game
        return {
            'changefirm_label': 'You chose Firm '+firm+' in the contest. \
        If given the choice again, would you still choose Firm '+firm+' or would you change your choice?'
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutFinalSurveyA = True


class PerformancePayment(CustomMturkPage):
    form_model = 'player'
    form_fields = ['time_PerformancePayment']
    # timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    def vars_for_template(self):
        return {
            'attempted': self.player.attempted,
            'correct': self.player.game1_score,
            'baseline_bonus': c(self.player.participant.vars['baseline_bonus']),
            'total_bonus': c(self.player.total_bonus),

            # automatically pluralizes the word 'problem' if necessary
            'problems': inflect.engine().plural('problem', self.player.attempted)
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutPayment = True


class Debrief(CustomMturkPage):
    form_model = 'player'
    form_fields = ['debriefComments','time_Debrief']
    # timeout_seconds = settings.SESSION_CONFIGS[0]['time_limit']

    def before_next_page(self):
        if self.timeout_happened:
            self.player.TimeoutDebrief = True


class CopyMturkCode(Page):
    def is_displayed(self):
        self.player.get_wait1()
        return 1
    pass


page_sequence = [
    Game1WaitPage,
    WhatHappensNextA,
    ChooseFirm,
    WhyFirm,
    Game1FirmWaitPage,
    Game1Firm,
    Game1,
    Results1WaitPage,
    SeeScoresChoice,
    Results1,
    FinalSurvey,
    FinalSurveyA,
    PerformancePayment,
    Debrief,
    CopyMturkCode
]
