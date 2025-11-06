# main/migrations/0009_create_savedevent_if_missing.py

from django.db import migrations

class Migration(migrations.Migration):
    # Keep the sequence intact, but do nothing here because
    # SavedEvent is already created in 0001_initial.
    dependencies = [
        ("main", "0008_create_payment"),
    ]

    operations = [
        # no-op on purpose
    ]
