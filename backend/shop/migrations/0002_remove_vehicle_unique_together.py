# Generated migration - allow multiple vehicles per customer without VIN

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vehicle',
            unique_together=set(),
        ),
    ]
