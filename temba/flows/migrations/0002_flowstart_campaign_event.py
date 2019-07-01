# Generated by Django 2.1.8 on 2019-07-01 20:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("campaigns", "0001_initial"), ("flows", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="flowstart",
            name="campaign_event",
            field=models.ForeignKey(
                help_text="The campaign event which created this flow start",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="flow_starts",
                to="campaigns.CampaignEvent",
            ),
        )
    ]
