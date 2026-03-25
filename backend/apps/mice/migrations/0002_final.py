# Generated manually — minimal clean version
# ticket_tier_id already exists in DB from previous local migration
# Only adding client_visible which is the actual new field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectasset',
            name='client_visible',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='If True, visible to client via their portal',
            ),
        ),
    ]
