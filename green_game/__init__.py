from otree.api import *

doc = """
Two-player emission and production decision game with a simplified cap-and-trade mechanism.
"""


class C(BaseConstants):
    NAME_IN_URL = 'green_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10

    # Final calibrated parameters
    a = 40
    c_quota = 47
    gamma0 = 5
    beta = 0.6

    # Carbon price
    carbon_price = 15


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    q = models.IntegerField(
        min=0,
        max=15,
        label="Please choose your production quantity q (0–15):"
    )

    g = models.IntegerField(
        min=1,
        max=5,
        label="Please choose your emission level g (1–5):"
    )

    price = models.FloatField()
    emission = models.FloatField()
    revenue = models.FloatField()
    carbon = models.FloatField()
    abate_cost = models.FloatField()
    profit = models.FloatField()

    def role(self):
        return f"Manufacturer {self.id_in_group}"


def set_payoffs(group: Group):
    p1, p2 = group.get_players()

    a = C.a
    k = C.carbon_price
    c_quota = C.c_quota
    gamma0 = C.gamma0
    beta = C.beta

    price = max(0, a - p1.q - p2.q)

    e1 = p1.q * p1.g
    e2 = p2.q * p2.g

    carbon1 = k * (c_quota - e1)
    carbon2 = k * (c_quota - e2)

    abate1 = beta * (gamma0 - p1.g) ** 2 * p1.q
    abate2 = beta * (gamma0 - p2.g) ** 2 * p2.q

    revenue1 = price * p1.q
    revenue2 = price * p2.q

    profit1 = revenue1 + carbon1 - abate1
    profit2 = revenue2 + carbon2 - abate2

    p1.price = price
    p1.emission = e1
    p1.revenue = revenue1
    p1.carbon = carbon1
    p1.abate_cost = abate1
    p1.profit = profit1

    p2.price = price
    p2.emission = e2
    p2.revenue = revenue2
    p2.carbon = carbon2
    p2.abate_cost = abate2
    p2.profit = profit2


class Decision(Page):
    form_model = 'player'
    form_fields = ['q', 'g']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            current_k=C.carbon_price,
            my_role=player.role(),
            c_quota=C.c_quota,
            gamma0=C.gamma0,
            beta=C.beta,
        )


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        other = player.get_others_in_group()[0]

        return dict(
            my_q=player.q,
            my_g=player.g,
            other_q=other.q,
            other_g=other.g,
            price=player.price,
            emission=player.emission,
            revenue=player.revenue,
            carbon=player.carbon,
            abate=player.abate_cost,
            profit=player.profit,
            round_number=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            current_k=C.carbon_price,
            my_role=player.role(),
            other_role=other.role(),
            c_quota=C.c_quota,
            gamma0=C.gamma0,
            beta=C.beta,
        )


page_sequence = [Decision, ResultsWaitPage, Results]
