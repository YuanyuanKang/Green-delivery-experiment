from os import environ

SESSION_CONFIGS = [
    dict(
        name='green_random',
        display_name='Green Game - Random Matching (k=2 to k=10)',
        num_demo_participants=6,
        app_sequence=['green_game'],
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
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'admin')

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', '123456789')

INSTALLED_APPS = ['otree']

ROOMS = [
    dict(
        name='green_room_random',
        display_name='Green Room - Random Matching',
        participant_label_file='_rooms/green_room_random.txt',
    ),
]
