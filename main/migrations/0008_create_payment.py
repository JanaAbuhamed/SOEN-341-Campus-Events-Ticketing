# main/migrations/0008_create_payment.py
from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_ticket_checked_in_at_ticket_claimed_at_and_more'),
        # ^^^ if your latest migration filename is different, update this
        # to match the most recent file in main/migrations.
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('status', models.CharField(choices=[('succeeded', 'Succeeded'), ('failed', 'Failed'), ('pending', 'Pending')], default='succeeded', max_length=16)),
                ('txn_id', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='main.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='main.user')),
            ],
            options={
                'unique_together': {('user', 'event')},
            },
        ),
    ]
