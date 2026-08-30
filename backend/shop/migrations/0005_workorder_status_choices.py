# Generated migration - update work order status choices

from django.db import migrations, models


def migrate_status_values(apps, schema_editor):
    WorkOrder = apps.get_model("shop", "WorkOrder")
    WorkOrder.objects.filter(status="pending").update(status="waiting_customer_approval")
    WorkOrder.objects.filter(status="cancelled").update(status="completed")


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_workorder_estimated_time_hours_workorder_rate"),
    ]

    operations = [
        # Widen column first so new status values fit (varchar 20 -> 30)
        migrations.AlterField(
            model_name="workorder",
            name="status",
            field=models.CharField(
                choices=[
                    ("waiting_customer_approval", "Waiting on customer approval"),
                    ("waiting_parts", "Waiting on parts"),
                    ("in_progress", "In progress"),
                    ("ready_pickup", "Ready for pickup"),
                    ("completed", "Completed"),
                ],
                default="waiting_customer_approval",
                max_length=30,
            ),
        ),
        migrations.RunPython(migrate_status_values, migrations.RunPython.noop),
    ]
