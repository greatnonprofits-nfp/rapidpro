# Generated by Django 2.2.4 on 2020-05-11 20:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flows', '0228_exportflowimagestask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flowimage',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='flowimage',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='flowimage',
            name='modified_by',
        ),
    ]