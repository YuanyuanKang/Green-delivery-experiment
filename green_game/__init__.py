from otree.api import *

doc = ""


class C(BaseConstants):
    NAME_IN_URL = 'green_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10


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

    emission = models.FloatField()
    revenue = models.FloatField()
    carbon = models.FloatField()
    abate_cost = models.FloatField()
    profit = models.FloatField()

    def role(self):
        return f"Manufacturer {self.id_in_group}"


def set_payoffs(group: Group):
    p1, p2 = group.get_players()

    # Parameters
    a = 20
    k = 2 if group.round_number <= 5 else 10
    c_quota = 20
    gamma0 = 5
    beta = 1

    # Common market price (same for both players)
    price = max(0, a - p1.q - p2.q)

    # Emissions
    e1 = p1.q * p1.g
    e2 = p2.q * p2.g

    # Carbon cost
    carbon1 = k * max(0, e1 - c_quota)
    carbon2 = k * max(0, e2 - c_quota)

    # Abatement cost
    abate1 = beta * (gamma0 - p1.g) ** 2 * p1.q
    abate2 = beta * (gamma0 - p2.g) ** 2 * p2.q

    # Revenue
    revenue1 = price * p1.q
    revenue2 = price * p2.q

    # Profit
    profit1 = revenue1 - carbon1 - abate1
    profit2 = revenue2 - carbon2 - abate2

    # Store results
    p1.emission = e1
    p2.emission = e2

    p1.revenue = revenue1
    p2.revenue = revenue2

    p1.carbon = carbon1
    p2.carbon = carbon2

    p1.abate_cost = abate1
    p2.abate_cost = abate2

    p1.profit = profit1
    p2.profit = profit2


class Decision(Page):
    form_model = 'player'
    form_fields = ['q', 'g']

    @staticmethod
    def vars_for_template(player: Player):
        current_k = 2 if player.round_number <= 5 else 10
        return dict(
            round_number=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            current_k=current_k,
            my_role=player.role(),
        )


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        other = player.get_others_in_group()[0]
        current_k = 2 if player.round_number <= 5 else 10

        return dict(
            my_q=player.q,
            my_g=player.g,
            other_q=other.q,
            other_g=other.g,
            emission=player.emission,
            revenue=player.revenue,
            carbon=player.carbon,
            abate=player.abate_cost,
            profit=player.profit,
            round_number=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            current_k=current_k,
            my_role=player.role(),
            other_role=other.role(),
        )


page_sequence = [Decision, ResultsWaitPage, Results]
