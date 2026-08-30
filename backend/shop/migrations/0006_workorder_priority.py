from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_workorder_status_choices"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="workorder",
            options={"ordering": ["-priority", "-created_at"]},
        ),
        migrations.AddField(
            model_name="workorder",
            name="priority",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Low"), (2, "Normal"), (3, "High"), (4, "Urgent")],
                db_index=True,
                default=2,
            ),
        ),
    ]
