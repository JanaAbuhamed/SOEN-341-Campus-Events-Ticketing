from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration keeps the sequence intact but performs no operation.
    The SavedEvent model already exists from 0001_initial.
    """

    dependencies = [
        ("main", "0008_create_payment"),
    ]

    operations = [
        # no-op on purpose
    ]
