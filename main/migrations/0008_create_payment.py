# main/migrations/0008_create_payment.py

from django.db import migrations

class Migration(migrations.Migration):
    # Keep the sequence intact, but do nothing here because
    # Payment is already created in 0001_initial.
    dependencies = [
        ("main", "0007_ticket_checked_in_at_ticket_claimed_at_and_more"),
    ]

    operations = [
        # no-op on purpose
    ]
