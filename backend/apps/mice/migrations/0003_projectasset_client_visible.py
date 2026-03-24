# apps/mice/migrations/0003_projectasset_client_visible.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mice', '0002_add_ticket_tier_id_to_subevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectasset',
            name='client_visible',
            field=models.BooleanField(
                default=False,
                help_text='If True, this asset is visible to the client via their portal',
                db_index=True,
            ),
        ),
    ]
