from os import environ


# ============================================================
# SESSION CONFIGURATIONS
# ============================================================

SESSION_CONFIGS = [
    dict(
        name='frc_pilot_v01',
        display_name='FRC Pilot V0.1 - Ultra-fast Delivery',

        # This is only the default number used on the oTree demo page.
        # It does NOT restrict the number of participants in a Room session.
        num_demo_participants=8,

        app_sequence=[
            'green_game',
        ],
    ),
]


# ============================================================
# DEFAULT SESSION SETTINGS
# ============================================================

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)


# ============================================================
# PARTICIPANT / SESSION FIELDS
# ============================================================

PARTICIPANT_FIELDS = []

SESSION_FIELDS = []


# ============================================================
# LANGUAGE AND CURRENCY
# ============================================================

LANGUAGE_CODE = 'en'

REAL_WORLD_CURRENCY_CODE = 'USD'

USE_POINTS = True


# ============================================================
# ADMIN SETTINGS
# ============================================================

ADMIN_USERNAME = 'admin'

ADMIN_PASSWORD = environ.get(
    'OTREE_ADMIN_PASSWORD',
    'admin'
)


# ============================================================
# DEMO PAGE
# ============================================================

DEMO_PAGE_INTRO_HTML = ""


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = environ.get(
    'OTREE_SECRET_KEY',
    '123456789'
)


# ============================================================
# INSTALLED APPS
# ============================================================

INSTALLED_APPS = [
    'otree',
]


# ============================================================
# ROOMS
# ============================================================

ROOMS = [
    dict(
        name='frc_pilot_room',
        display_name='FRC Pilot Room',
    ),
]
