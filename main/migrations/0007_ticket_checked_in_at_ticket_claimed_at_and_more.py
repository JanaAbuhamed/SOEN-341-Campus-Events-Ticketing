# main/migrations/0007_ticket_checked_in_at_ticket_claimed_at_and_more.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),   # ← was 0006_merge_..., which doesn't exist here
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="checked_in_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="claimed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="first_scanned_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="last_scanned_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="qr_token",
            field=models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="scan_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
