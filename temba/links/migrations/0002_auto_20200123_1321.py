# Generated by Django 2.1.9 on 2020-01-23 13:21

from django.db import migrations
import temba.utils.models


class Migration(migrations.Migration):

    dependencies = [("links", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="destination",
            field=temba.utils.models.URLTextField(help_text="The destination URL for this trackable link"),
        )
    ]
