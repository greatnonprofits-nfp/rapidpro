# Generated by Django 2.2.4 on 2020-12-11 13:01

import django.contrib.postgres.fields
from django.db import migrations, models


def add_parent_org_admins(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Org = apps.get_model("orgs", "Org")
    nested_orgs = Org.objects.using(db_alias).exclude(parent__isnull=True)
    for org in nested_orgs:
        org.administrators.add(*org.parent.administrators.all())


def remove_parent_org_admins(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Org = apps.get_model("orgs", "Org")
    nested_orgs = Org.objects.using(db_alias).exclude(parent__isnull=True)
    for org in nested_orgs:
        org.administrators.clear()
        if org.created_by not in org.administrators.all():
            org.administrators.add(org.created_by)


class Migration(migrations.Migration):

    replaces = [
        ("orgs", "0059_creditalert_admin_emails"),
        ("orgs", "0059_usersettings_authy_id"),
        ("orgs", "0060_merge_20200510_1733"),
        ("orgs", "0061_data_move_admins_to_nested_org"),
    ]

    dependencies = [("orgs", "0058_auto_20190723_2129")]

    operations = [
        migrations.AddField(
            model_name="creditalert",
            name="admin_emails",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.EmailField(max_length=254),
                default=list,
                help_text="Emails of administrators who will be alerted",
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="authy_id",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Authy ID"),
        ),
        migrations.RunPython(code=add_parent_org_admins, reverse_code=remove_parent_org_admins),
    ]