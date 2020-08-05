# Generated by Django 2.1.3 on 2018-11-27 21:24

from django.db import migrations, models


def remove_plugin_models(apps, schema_editor):
    """Remove the models for djangoplugins app that has been removed"""

    schema_editor.execute("DROP TABLE IF EXISTS djangoplugins_plugin")
    schema_editor.execute("DROP TABLE IF EXISTS djangoplugins_pluginpoint")


class Migration(migrations.Migration):
    dependencies = [
        ('django_basin3d', '0003_remove_measurement_approach'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='datasource',
            name='plugin_class',
            field=models.TextField(blank=True)
        ),
        migrations.AddField(
            model_name='datasource',
            name='plugin_module',
            field=models.TextField(blank=True)
        ),
        migrations.RemoveField(model_name='datasource',
                               name='plugin_id'),
        migrations.RunPython(remove_plugin_models)
    ]