# Generated by Django 2.2.10 on 2020-08-26 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("contacts", "0121_auto_20200825_2000")]

    operations = [
        migrations.AlterField(
            model_name="contactgroup",
            name="group_type",
            field=models.CharField(
                choices=[
                    ("A", "Active"),
                    ("B", "Blocked"),
                    ("S", "Stopped"),
                    ("V", "Archived"),
                    ("U", "User Defined Groups"),
                ],
                default="U",
                help_text="What type of group it is, either user defined or one of our system groups",
                max_length=1,
            ),
        )
    ]
