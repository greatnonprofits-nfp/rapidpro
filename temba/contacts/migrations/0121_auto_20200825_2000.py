# Generated by Django 2.2.10 on 2020-08-25 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("contacts", "0120_auto_20200825_1624")]

    operations = [
        migrations.RemoveField(model_name="contact", name="is_blocked"),
        migrations.RemoveField(model_name="contact", name="is_stopped"),
    ]
