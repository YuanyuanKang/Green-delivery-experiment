from os import environ

SESSION_CONFIGS = [
    dict(
        name='green_low',
        display_name='Green Delivery Game - Low Carbon Price',
        num_demo_participants=2,
        app_sequence=['green_game'],
        carbon_price=1,
    ),
    dict(
        name='green_high',
        display_name='Green Delivery Game - High Carbon Price',
        num_demo_participants=2,
        app_sequence=['green_game'],
        carbon_price=3,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = '123456789'

INSTALLED_APPS = ['otree']

ROOMS = [
    dict(
        name='green_room_low',
        display_name='Green Delivery Room - Low Carbon Price',
    ),
    dict(
        name='green_room_high',
        display_name='Green Delivery Room - High Carbon Price',
    ),
]
