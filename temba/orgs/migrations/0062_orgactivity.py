# Generated by Django 2.2.4 on 2020-05-12 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("orgs", "0061_auto_20200506_2038")]

    operations = [
        migrations.CreateModel(
            name="OrgActivity",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.DateField()),
                ("contact_count", models.IntegerField(default=0)),
                ("active_contact_count", models.IntegerField(default=0)),
                ("outgoing_count", models.IntegerField(default=0)),
                ("incoming_count", models.IntegerField(default=0)),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="contact_activity", to="orgs.Org"
                    ),
                ),
            ],
            options={"unique_together": {("org", "day")}},
        )
    ]