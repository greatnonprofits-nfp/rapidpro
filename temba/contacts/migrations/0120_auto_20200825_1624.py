# Generated by Django 2.2.10 on 2020-08-25 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("contacts", "0119_update_sysgroup_trigger")]

    operations = [
        migrations.AlterField(
            model_name="contact", name="is_blocked", field=models.BooleanField(default=False, null=True)
        ),
        migrations.AlterField(
            model_name="contact", name="is_stopped", field=models.BooleanField(default=False, null=True)
        ),
    ]
