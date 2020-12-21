# Generated by Django 2.2.4 on 2020-12-11 11:55

from django.db import migrations
import temba.utils.models


class Migration(migrations.Migration):

    replaces = [('campaigns', '0035_auto_20200313_1150'), ('campaigns', '0036_auto_20200402_1534'), ('campaigns', '0037_campaignevent_extra'), ('campaigns', '0038_auto_20200428_2109')]

    dependencies = [
        ('campaigns', '0034_merge_20200313_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignevent',
            name='message',
            field=temba.utils.models.TranslatableField(max_length=640, null=True),
        ),
        migrations.AddField(
            model_name='campaignevent',
            name='extra',
            field=temba.utils.models.JSONAsTextField(blank=True, default=dict, null=True),
        ),
    ]