from otree.api import *
import random
import time


doc = """
Two-player competitive ultra-fast delivery experiment.

Participants act as e-commerce platform operations managers and choose
a Fulfilment Resource Commitment (FRC) level under different market-demand
and carbon-pricing conditions.

Pilot V0.1:
- 2 practice rounds
- 18 formal rounds
- blocked within-subject carbon pricing
- counterbalanced carbon-price order
- controlled demand randomisation
- anonymous random rematching
"""


# ============================================================
# CONSTANTS
# ============================================================

class C(BaseConstants):
    NAME_IN_URL = 'frc_game'
    PLAYERS_PER_GROUP = 2

    NUM_PRACTICE_ROUNDS = 2
    NUM_FORMAL_ROUNDS = 18
    NUM_ROUNDS = 20

    FORMAL_ROUNDS_PER_BLOCK = 9

    # Demand
    DEMAND_LOW = 800
    DEMAND_MEDIUM = 1000
    DEMAND_HIGH = 1200

    # Revenue
    REVENUE_PER_ORDER = 1

    # Carbon pricing
    CARBON_PRICE_LOW = 1
    CARBON_PRICE_HIGH = 4

    # Fulfilment costs
    FRC_COST_LOW = 120
    FRC_COST_MEDIUM = 150
    FRC_COST_HIGH = 180

    # Base emissions
    BASE_EMISSION_LOW = 2
    BASE_EMISSION_MEDIUM = 4
    BASE_EMISSION_HIGH = 7

    # Variable emissions
    EMISSION_PER_ORDER = 0.015


# ============================================================
# MODELS
# ============================================================

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Experimental structure
    # --------------------------------------------------------

    sequence = models.StringField()
    # A = Low CP -> High CP
    # B = High CP -> Low CP

    block = models.IntegerField()
    formal_round = models.IntegerField()
    is_practice = models.BooleanField()

    # Experimental conditions
    demand_state = models.StringField()
    market_demand = models.IntegerField()

    carbon_condition = models.StringField()
    carbon_price = models.FloatField()

    # Decision
    frc = models.StringField(
        choices=[
            ['Low', 'Low FRC'],
            ['Medium', 'Medium FRC'],
            ['High', 'High FRC'],
        ],
        widget=widgets.RadioSelect,
        label='Choose your Fulfilment Resource Commitment (FRC):'
    )

    # Opponent information
    opponent_id = models.IntegerField()
    pair_id = models.IntegerField()
    opponent_frc = models.StringField()

    # Delivery performance
    delivery_performance = models.FloatField()
    opponent_delivery_performance = models.FloatField()
    performance_difference = models.FloatField()

    # Market outcome
    market_share = models.FloatField()
    orders_received = models.IntegerField()

    # Economic outcome
    revenue = models.FloatField()
    fulfilment_cost = models.FloatField()

    # Environmental outcome
    base_emission = models.FloatField()
    order_emission = models.FloatField()
    total_emission = models.FloatField()
    carbon_cost = models.FloatField()

    # Final outcome
    profit = models.FloatField()

    # Decision time
    decision_started_at = models.FloatField()
    decision_time = models.FloatField()

    # Comprehension check
    check_objective = models.StringField(
        choices=[
            ['profit', 'Maximise my platform profit'],
            ['orders', 'Always maximise the number of orders'],
            ['emissions', 'Always minimise emissions'],
            ['beat', 'Always earn more than the competitor'],
        ],
        widget=widgets.RadioSelect,
        label='What is your main objective in the game?'
    )

    check_opponent = models.StringField(
        choices=[
            ['yes', 'Yes'],
            ['no', 'No'],
        ],
        widget=widgets.RadioSelect,
        label=(
            'When choosing your FRC, can you see the competitor’s '
            'current FRC choice?'
        )
    )

    check_high_frc = models.StringField(
        choices=[
            ['always', 'Yes, High FRC always gives the highest profit'],
            [
                'tradeoff',
                'No, higher FRC can improve delivery performance but also costs more'
            ],
        ],
        widget=widgets.RadioSelect,
        label='Does choosing High FRC always give the highest profit?'
    )

    check_delivery = models.StringField(
        choices=[
            [
                'more_orders',
                'The better-performing platform receives a larger share of market orders'
            ],
            [
                'no_effect',
                'Delivery performance does not affect market allocation'
            ],
        ],
        widget=widgets.RadioSelect,
        label=(
            'What happens if one platform has better delivery performance '
            'than the other?'
        )
    )

    check_carbon = models.StringField(
        choices=[
            [
                'reduces_profit',
                'Carbon Cost is deducted when profit is calculated'
            ],
            [
                'increases_profit',
                'Carbon Cost increases profit'
            ],
            [
                'irrelevant',
                'Carbon Cost has no effect on profit'
            ],
        ],
        widget=widgets.RadioSelect,
        label='How does Carbon Cost affect your platform profit?'
    )

    check_profit = models.IntegerField(
        label=(
            'Example: Revenue = 300 points, Fulfilment Cost = 100 points, '
            'Carbon Cost = 20 points. What is Profit?'
        )
    )


# ============================================================
# PARAMETER LOOKUPS
# ============================================================

def demand_value(demand_state):
    values = {
        'Low': C.DEMAND_LOW,
        'Medium': C.DEMAND_MEDIUM,
        'High': C.DEMAND_HIGH,
    }
    return values[demand_state]


def carbon_price_value(condition):
    values = {
        'Low': C.CARBON_PRICE_LOW,
        'High': C.CARBON_PRICE_HIGH,
    }
    return values[condition]


def frc_cost(frc):
    values = {
        'Low': C.FRC_COST_LOW,
        'Medium': C.FRC_COST_MEDIUM,
        'High': C.FRC_COST_HIGH,
    }
    return values[frc]


def base_emission_value(frc):
    values = {
        'Low': C.BASE_EMISSION_LOW,
        'Medium': C.BASE_EMISSION_MEDIUM,
        'High': C.BASE_EMISSION_HIGH,
    }
    return values[frc]


# ============================================================
# DELIVERY PERFORMANCE
# ============================================================

def get_delivery_performance(demand_state, frc):

    matrix = {
        'Low': {
            'Low': 90,
            'Medium': 96,
            'High': 99,
        },

        'Medium': {
            'Low': 80,
            'Medium': 90,
            'High': 96,
        },

        'High': {
            'Low': 70,
            'Medium': 80,
            'High': 90,
        },
    }

    return matrix[demand_state][frc]


# ============================================================
# CUSTOMER ALLOCATION
# ============================================================

def better_platform_share(dp_difference):

    if dp_difference == 0:
        return 0.50

    if 1 <= dp_difference <= 5:
        return 0.52

    if 6 <= dp_difference <= 10:
        return 0.55

    if 11 <= dp_difference <= 20:
        return 0.58

    raise ValueError(
        f'Unexpected Delivery Performance difference: {dp_difference}'
    )


# ============================================================
# CONTROLLED DEMAND RANDOMISATION
# ============================================================

def get_demand_schedule(session_code, block_number):

    """
    Each formal block contains exactly:
    3 Low + 3 Medium + 3 High Demand rounds.

    The order is randomised once at session level.
    """

    schedule = (
        ['Low'] * 3
        + ['Medium'] * 3
        + ['High'] * 3
    )

    rng = random.Random(
        f'{session_code}-demand-block-{block_number}'
    )

    rng.shuffle(schedule)

    return schedule


# ============================================================
# COUNTERBALANCED SEQUENCE ASSIGNMENT
# ============================================================

def get_sequence_assignments(subsession):

    """
    Randomly and evenly assigns participants:

    Sequence A:
    Low CP -> High CP

    Sequence B:
    High CP -> Low CP

    Session size must be divisible by 4 so that each
    sequence pool contains an even number of participants.
    """

    players = subsession.get_players()
    n = len(players)

    if n % 4 != 0:
        raise ValueError(
            'FRC pilot requires a session size divisible by 4 '
            '(for example 4, 8, 12, 16, ... participants).'
        )

    participant_ids = [
        p.participant.id_in_session
        for p in players
    ]

    participant_ids.sort()

    rng = random.Random(
        f'{subsession.session.code}-sequence'
    )

    rng.shuffle(participant_ids)

    half = n // 2

    sequence_a_ids = set(
        participant_ids[:half]
    )

    assignments = {}

    for participant_id in participant_ids:

        if participant_id in sequence_a_ids:
            assignments[participant_id] = 'A'
        else:
            assignments[participant_id] = 'B'

    return assignments


# ============================================================
# MATCHING
# ============================================================

def previous_opponent_id(player):

    if player.round_number <= 1:
        return None

    previous_player = player.in_round(
        player.round_number - 1
    )

    others = previous_player.get_others_in_group()

    if not others:
        return None

    return others[0].participant.id_in_session


def make_random_pairs(
    players,
    session_code,
    round_number,
    pool_name,
    avoid_previous=True,
):

    """
    Randomly pairs participants within the same sequence pool.

    Where possible, avoid matching the same opponent
    in two consecutive rounds.
    """

    if len(players) % 2 != 0:
        raise ValueError(
            f'Cannot pair an odd number of players '
            f'in matching pool {pool_name}.'
        )

    rng = random.Random(
        f'{session_code}-round-{round_number}-{pool_name}'
    )

    original = list(players)
    best_pairs = None

    for _ in range(500):

        shuffled = list(original)
        rng.shuffle(shuffled)

        pairs = [
            [shuffled[i], shuffled[i + 1]]
            for i in range(0, len(shuffled), 2)
        ]

        best_pairs = pairs

        if not avoid_previous or len(players) < 4:
            break

        repeated_match = False

        for p1, p2 in pairs:

            p1_previous = previous_opponent_id(p1)
            p2_previous = previous_opponent_id(p2)

            if (
                p1_previous == p2.participant.id_in_session
                or
                p2_previous == p1.participant.id_in_session
            ):
                repeated_match = True
                break

        if not repeated_match:
            break

    return [
        [
            p1.id_in_subsession,
            p2.id_in_subsession,
        ]
        for p1, p2 in best_pairs
    ]


# ============================================================
# SESSION CREATION
# ============================================================

def creating_session(subsession: Subsession):

    players = subsession.get_players()

    # --------------------------------------------------------
    # 1. Fixed counterbalanced sequence assignment
    # --------------------------------------------------------

    if subsession.round_number == 1:

        sequence_assignments = get_sequence_assignments(
            subsession
        )

        for player in players:

            player.participant.vars['frc_sequence'] = (
                sequence_assignments[
                    player.participant.id_in_session
                ]
            )

    for player in players:

        player.sequence = (
            player.participant.vars['frc_sequence']
        )

    # --------------------------------------------------------
    # 2. PRACTICE ROUND 1
    # --------------------------------------------------------

    if subsession.round_number == 1:

        for player in players:

            player.is_practice = True
            player.formal_round = 0
            player.block = 0

            player.demand_state = 'Medium'
            player.market_demand = C.DEMAND_MEDIUM

            player.carbon_condition = 'Low'
            player.carbon_price = C.CARBON_PRICE_LOW

        subsession.group_randomly()

        return

    # --------------------------------------------------------
    # 3. PRACTICE ROUND 2
    # --------------------------------------------------------

    if subsession.round_number == 2:

        for player in players:

            player.is_practice = True
            player.formal_round = 0
            player.block = 0

            player.demand_state = 'High'
            player.market_demand = C.DEMAND_HIGH

            player.carbon_condition = 'High'
            player.carbon_price = C.CARBON_PRICE_HIGH

        subsession.group_randomly()

        return

    # --------------------------------------------------------
    # 4. FORMAL ROUND NUMBER
    # --------------------------------------------------------

    formal_round = (
        subsession.round_number
        - C.NUM_PRACTICE_ROUNDS
    )

    # --------------------------------------------------------
    # 5. FORMAL BLOCK
    # --------------------------------------------------------

    if formal_round <= C.FORMAL_ROUNDS_PER_BLOCK:

        block = 1
        position_in_block = formal_round - 1

    else:

        block = 2

        position_in_block = (
            formal_round
            - C.FORMAL_ROUNDS_PER_BLOCK
            - 1
        )

    # --------------------------------------------------------
    # 6. DEMAND SCHEDULE
    # --------------------------------------------------------

    demand_schedule = get_demand_schedule(
        subsession.session.code,
        block
    )

    current_demand = demand_schedule[
        position_in_block
    ]

    # --------------------------------------------------------
    # 7. DEMAND + CARBON CONDITION
    # --------------------------------------------------------

    for player in players:

        player.is_practice = False
        player.formal_round = formal_round
        player.block = block

        player.demand_state = current_demand

        player.market_demand = demand_value(
            current_demand
        )

        if player.sequence == 'A':

            if block == 1:
                carbon_condition = 'Low'
            else:
                carbon_condition = 'High'

        else:

            if block == 1:
                carbon_condition = 'High'
            else:
                carbon_condition = 'Low'

        player.carbon_condition = carbon_condition

        player.carbon_price = carbon_price_value(
            carbon_condition
        )

    # --------------------------------------------------------
    # 8. RANDOM REMATCHING WITHIN CURRENT CP CONDITION
    # --------------------------------------------------------

    sequence_a_players = [
        p for p in players
        if p.sequence == 'A'
    ]

    sequence_b_players = [
        p for p in players
        if p.sequence == 'B'
    ]

    pairs_a = make_random_pairs(
        players=sequence_a_players,
        session_code=subsession.session.code,
        round_number=subsession.round_number,
        pool_name='A',
        avoid_previous=True,
    )

    pairs_b = make_random_pairs(
        players=sequence_b_players,
        session_code=subsession.session.code,
        round_number=subsession.round_number,
        pool_name='B',
        avoid_previous=True,
    )

    new_group_matrix = (
        pairs_a + pairs_b
    )

    subsession.set_group_matrix(
        new_group_matrix
    )


# ============================================================
# PAYOFF ENGINE
# ============================================================

def set_payoffs(group: Group):

    p1, p2 = group.get_players()

    if p1.market_demand != p2.market_demand:
        raise ValueError(
            'Matched players have different market demand.'
        )

    if p1.carbon_price != p2.carbon_price:
        raise ValueError(
            'Matched players have different carbon prices.'
        )

    demand_state = p1.demand_state
    total_demand = p1.market_demand
    carbon_price = p1.carbon_price

    p1.delivery_performance = get_delivery_performance(
        demand_state,
        p1.frc
    )

    p2.delivery_performance = get_delivery_performance(
        demand_state,
        p2.frc
    )

    p1.opponent_delivery_performance = (
        p2.delivery_performance
    )

    p2.opponent_delivery_performance = (
        p1.delivery_performance
    )

    p1.opponent_frc = p2.frc
    p2.opponent_frc = p1.frc

    p1.opponent_id = (
        p2.participant.id_in_session
    )

    p2.opponent_id = (
        p1.participant.id_in_session
    )

    p1.pair_id = group.id_in_subsession
    p2.pair_id = group.id_in_subsession

    difference = abs(
        p1.delivery_performance
        - p2.delivery_performance
    )

    p1.performance_difference = difference
    p2.performance_difference = difference

    if difference == 0:

        p1.market_share = 0.50
        p2.market_share = 0.50

    else:

        winner_share = better_platform_share(
            difference
        )

        loser_share = 1 - winner_share

        if (
            p1.delivery_performance
            > p2.delivery_performance
        ):

            p1.market_share = winner_share
            p2.market_share = loser_share

        else:

            p1.market_share = loser_share
            p2.market_share = winner_share

    p1.orders_received = int(
        round(
            total_demand
            * p1.market_share
        )
    )

    p2.orders_received = int(
        round(
            total_demand
            * p2.market_share
        )
    )

    if (
        p1.orders_received
        + p2.orders_received
        != total_demand
    ):
        raise ValueError(
            'Allocated orders do not equal total market demand.'
        )

    p1.revenue = round(
        p1.orders_received
        * C.REVENUE_PER_ORDER,
        2
    )

    p2.revenue = round(
        p2.orders_received
        * C.REVENUE_PER_ORDER,
        2
    )

    p1.fulfilment_cost = frc_cost(
        p1.frc
    )

    p2.fulfilment_cost = frc_cost(
        p2.frc
    )

    p1.base_emission = base_emission_value(
        p1.frc
    )

    p2.base_emission = base_emission_value(
        p2.frc
    )

    p1.order_emission = round(
        p1.orders_received
        * C.EMISSION_PER_ORDER,
        4
    )

    p2.order_emission = round(
        p2.orders_received
        * C.EMISSION_PER_ORDER,
        4
    )

    p1.total_emission = round(
        p1.base_emission
        + p1.order_emission,
        4
    )

    p2.total_emission = round(
        p2.base_emission
        + p2.order_emission,
        4
    )

    p1.carbon_cost = round(
        carbon_price
        * p1.total_emission,
        2
    )

    p2.carbon_cost = round(
        carbon_price
        * p2.total_emission,
        2
    )

    p1.profit = round(
        p1.revenue
        - p1.fulfilment_cost
        - p1.carbon_cost,
        2
    )

    p2.profit = round(
        p2.revenue
        - p2.fulfilment_cost
        - p2.carbon_cost,
        2
    )

    if p1.is_practice:
        p1.payoff = cu(0)
    else:
        p1.payoff = cu(p1.profit)

    if p2.is_practice:
        p2.payoff = cu(0)
    else:
        p2.payoff = cu(p2.profit)


# ============================================================
# COMPREHENSION CHECK
# ============================================================

class ComprehensionCheck(Page):

    form_model = 'player'

    form_fields = [
        'check_objective',
        'check_opponent',
        'check_high_frc',
        'check_delivery',
        'check_carbon',
        'check_profit',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):

        correct = (
            values['check_objective'] == 'profit'
            and values['check_opponent'] == 'no'
            and values['check_high_frc'] == 'tradeoff'
            and values['check_delivery'] == 'more_orders'
            and values['check_carbon'] == 'reduces_profit'
            and values['check_profit'] == 180
        )

        if not correct:
            return (
                'One or more answers are incorrect. '
                'Please review the rules and try again.'
            )


# ============================================================
# INTRO PAGES
# ============================================================

class PracticeIntro(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class BlockIntro(Page):

    @staticmethod
    def is_displayed(player: Player):

        return (
            player.round_number
            == C.NUM_PRACTICE_ROUNDS + 1
        )

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            carbon_condition=player.carbon_condition,
            carbon_price=player.carbon_price,
        )


class BlockTransition(Page):

    @staticmethod
    def is_displayed(player: Player):

        return (
            player.round_number
            ==
            C.NUM_PRACTICE_ROUNDS
            + C.FORMAL_ROUNDS_PER_BLOCK
            + 1
        )

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            carbon_condition=player.carbon_condition,
            carbon_price=player.carbon_price,
        )


# ============================================================
# DECISION PAGE
# ============================================================

class Decision(Page):

    form_model = 'player'
    form_fields = ['frc']

    @staticmethod
    def vars_for_template(player: Player):

        started = player.field_maybe_none(
            'decision_started_at'
        )

        if started is None:
            player.decision_started_at = time.time()

        if player.is_practice:

            round_label = (
                f'Practice Round '
                f'{player.round_number} '
                f'of {C.NUM_PRACTICE_ROUNDS}'
            )

        else:

            round_label = (
                f'Formal Round '
                f'{player.formal_round} '
                f'of {C.NUM_FORMAL_ROUNDS}'
            )

        return dict(
            round_label=round_label,

            player_number=player.participant.id_in_session,

            is_practice=player.is_practice,

            demand_state=player.demand_state,
            market_demand=player.market_demand,

            carbon_condition=player.carbon_condition,
            carbon_price=player.carbon_price,

            frc_cost_low=C.FRC_COST_LOW,
            frc_cost_medium=C.FRC_COST_MEDIUM,
            frc_cost_high=C.FRC_COST_HIGH,

            delivery_performance_low=get_delivery_performance(
                player.demand_state,
                'Low'
            ),

            delivery_performance_medium=get_delivery_performance(
                player.demand_state,
                'Medium'
            ),

            delivery_performance_high=get_delivery_performance(
                player.demand_state,
                'High'
            ),

            revenue_per_order=C.REVENUE_PER_ORDER,

            base_emission_low=C.BASE_EMISSION_LOW,
            base_emission_medium=C.BASE_EMISSION_MEDIUM,
            base_emission_high=C.BASE_EMISSION_HIGH,

            emission_per_order=C.EMISSION_PER_ORDER,
        )

    @staticmethod
    def before_next_page(
        player: Player,
        timeout_happened
    ):

        started = player.field_maybe_none(
            'decision_started_at'
        )

        if started is not None:

            player.decision_time = round(
                time.time() - started,
                3
            )


# ============================================================
# WAIT PAGE
# ============================================================

class ResultsWaitPage(WaitPage):

    title_text = 'Waiting for competitor'

    body_text = (
        'Your decision has been submitted. '
        'Please wait for the competing platform.'
    )

    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group)


# ============================================================
# RESULTS PAGE
# ============================================================

class Results(Page):

    @staticmethod
    def vars_for_template(player: Player):

        opponent = (
            player.get_others_in_group()[0]
        )

        if player.is_practice:

            round_label = (
                f'Practice Round '
                f'{player.round_number} Results'
            )

        else:

            round_label = (
                f'Formal Round '
                f'{player.formal_round} Results'
            )

        return dict(
            round_label=round_label,

            player_number=player.participant.id_in_session,

            is_practice=player.is_practice,

            demand_state=player.demand_state,
            market_demand=player.market_demand,

            carbon_condition=player.carbon_condition,
            carbon_price=player.carbon_price,

            my_frc=player.frc,
            competitor_frc=opponent.frc,

            my_delivery_performance=(
                player.delivery_performance
            ),

            competitor_delivery_performance=(
                opponent.delivery_performance
            ),

            orders_received=player.orders_received,

            revenue=player.revenue,

            fulfilment_cost=player.fulfilment_cost,

            carbon_cost=player.carbon_cost,

            profit=player.profit,
        )


# ============================================================
# END PAGE
# ============================================================

class End(Page):

    @staticmethod
    def is_displayed(player: Player):

        return (
            player.round_number
            == C.NUM_ROUNDS
        )

    @staticmethod
    def vars_for_template(player: Player):

        formal_players = player.in_rounds(
            C.NUM_PRACTICE_ROUNDS + 1,
            C.NUM_ROUNDS,
        )

        total_formal_profit = round(
            sum(
                p.profit
                for p in formal_players
            ),
            2
        )

        return dict(
            total_formal_profit=total_formal_profit
        )


# ============================================================
# PAGE SEQUENCE
# ============================================================

page_sequence = [
    ComprehensionCheck,
    PracticeIntro,
    BlockIntro,
    BlockTransition,
    Decision,
    ResultsWaitPage,
    Results,
    End,
]
