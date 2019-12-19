# Generated by Django 2.1.9 on 2019-10-02 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flows", "0204_flowstart_campaign_event")]

    operations = [
        migrations.AlterField(
            model_name="ruleset",
            name="ruleset_type",
            field=models.CharField(
                choices=[
                    ("wait_message", "Wait for message"),
                    ("wait_menu", "Wait for USSD menu"),
                    ("wait_ussd", "Wait for USSD message"),
                    ("wait_recording", "Wait for recording"),
                    ("wait_digit", "Wait for digit"),
                    ("wait_digits", "Wait for digits"),
                    ("subflow", "Subflow"),
                    ("webhook", "Webhook"),
                    ("resthook", "Resthook"),
                    ("lookup", "Lookup"),
                    ("airtime", "Transfer Airtime"),
                    ("form_field", "Split by message form"),
                    ("contact_field", "Split on contact field"),
                    ("expression", "Split by expression"),
                    ("random", "Split Randomly"),
                ],
                help_text="The type of ruleset",
                max_length=16,
                null=True,
            ),
        )
    ]
