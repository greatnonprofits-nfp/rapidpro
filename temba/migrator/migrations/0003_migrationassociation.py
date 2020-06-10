# Generated by Django 2.2.4 on 2020-06-01 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("migrator", "0002_migrationtask_migration_org")]

    operations = [
        migrations.CreateModel(
            name="MigrationAssociation",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("old_id", models.PositiveIntegerField(verbose_name="The ID provided from live server")),
                ("new_id", models.PositiveIntegerField(verbose_name="The new ID generated on app server")),
                (
                    "model",
                    models.CharField(
                        choices=[
                            ("campaigns_campaign", "campaigns_campaign"),
                            ("campaigns_campaignevent", "campaigns_campaignevent"),
                            ("channels_channel", "channels_channel"),
                            ("contacts_contact", "contacts_contact"),
                            ("contacts_contacturn", "contacts_contacturn"),
                            ("contacts_contactgroup", "contacts_contactgroup"),
                            ("contacts_contactfield", "contacts_contactfield"),
                            ("msgs_msg", "msgs_msg"),
                            ("msgs_label", "msgs_label"),
                            ("flows_flow", "flows_flow"),
                            ("flows_flowlabel", "flows_flowlabel"),
                            ("flows_flowrun", "flows_flowrun"),
                            ("flows_flowstart", "flows_flowstart"),
                            ("links_link", "links_link"),
                            ("schedules_schedule", "schedules_schedule"),
                            ("orgs_topups", "orgs_topups"),
                            ("triggers_trigger", "triggers_trigger"),
                        ],
                        max_length=255,
                        verbose_name="Model related to the ID",
                    ),
                ),
                (
                    "migration_task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="associations",
                        to="migrator.MigrationTask",
                    ),
                ),
            ],
        )
    ]