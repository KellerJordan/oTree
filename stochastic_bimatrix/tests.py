from otree.api import Bot, Submission
from . import views

class PlayerBot(Bot):

    def play_round(self):
        yield views.Introduction
        yield Submission(views.Decision, {}, check_html=False)
        test_get_payoff()
        yield views.Results


    def validate_play(self):
        assert self.payoff > 0




def test_get_payoff():

    from otree_redwood.models import Event
    from otree.models.participant import Participant
    from otree.models.session import Session
    import random
    from django.utils import timezone
    from . import models

    sess = Session.objects.create(code=str(random.randint(0, 500000)))
    p1 = Participant.objects.create(session=sess, code='test_p1_'+str(random.randint(0, 500000)))
    p2 = Participant.objects.create(session=sess, code='test_p2_'+str(random.randint(0, 500000)))
    start = timezone.now()

    def create_event(channel, value, participant, timediff):
        Event.objects.create(
            session=sess,
            round=1,
            group=1,
            channel=channel,
            timestamp=start+timezone.timedelta(seconds=timediff),
            value=value,
            participant=participant,
        )

    create_event('decisions', 0.5, p1, 0)
    create_event('decisions', 0.5, p2, 0)
    create_event('decisions', 0.8, p2, 5)
    create_event('decisions', 0.9, p1, 10)
    create_event('transitions', 1, None, 12)
    create_event('decisions', 0.4, p1, 18)
    create_event('decisions', 0.7, p1, 20)
    create_event('decisions', None, p1, 120)
    create_event('decisions', None, p2, 120)


    events_over_time = Event.objects.filter(
        session=sess,
        round=1,
        group=1
    )
    payoff_grids = [
        [
            [ 100, 100 ], [   0, 800 ],
            [ 800,   0 ], [ 300, 300 ]
        ],
        [
            [ 800,   0 ], [   0, 200 ],
            [   0, 200 ], [ 200,   0 ]
        ]
    ]

    print('RUNNING GET_PAYOFF FOR PLAYER 1 ----------------------------------------------')
    payoff1 = models.get_payoff(events_over_time, 0, p1.code, payoff_grids)

    print('RUNNING GET_PAYOFF FOR PLAYER 2 ----------------------------------------------')
    payoff2 = models.get_payoff(events_over_time, 1, p2.code, payoff_grids)

    print('RESULTS ----------------------------------------------------------------------')
    assert 0 < payoff1 and payoff1 < 100000
    assert 0 < payoff2 and payoff2 < 100000
    assert abs(payoff1 - 90.25) < 1
    assert abs(payoff2 - 439.45) < 1
    print(payoff1, payoff2)
