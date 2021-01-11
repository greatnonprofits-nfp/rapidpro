# Generated by Django 2.2.10 on 2020-08-11 20:04

from django.db import migrations

FIELD_TYPE_SYSTEM = "S"
KEY_LAST_SEEN_ON = "last_seen_on"
TYPE_DATETIME = "D"


def add_last_seen_on_sys_field(apps, schema_editor):  # pragma: no cover
    Org = apps.get_model("orgs", "Org")
    for org in Org.objects.all():
        if not org.contactfields.filter(field_type=FIELD_TYPE_SYSTEM, key=KEY_LAST_SEEN_ON).exists():
            org.contactfields.create(
                field_type=FIELD_TYPE_SYSTEM,
                key=KEY_LAST_SEEN_ON,
                label="Last Seen On",
                value_type=TYPE_DATETIME,
                show_in_table=False,
                created_by=org.created_by,
                modified_by=org.modified_by,
            )


def reverse(apps, schema_editor):  # pragma: no cover
    ContactField = apps.get_model("contacts", "ContactField")
    ContactField.all_fields.filter(field_type=FIELD_TYPE_SYSTEM, key=KEY_LAST_SEEN_ON).delete()


class Migration(migrations.Migration):

    dependencies = [("contacts", "0111_populate_last_seen_on_2")]

    operations = [migrations.RunPython(add_last_seen_on_sys_field, reverse)]
