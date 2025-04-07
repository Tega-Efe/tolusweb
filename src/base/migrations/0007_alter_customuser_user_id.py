from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    CustomUser = apps.get_model('base', 'CustomUser')
    for user in CustomUser.objects.all():
        user.user_id = uuid.uuid4()
        user.save()

class Migration(migrations.Migration):
    dependencies = [
        ('base', '0006_add_uuids'),
    ]

    operations = [
        # First add the field
        migrations.AddField(
            model_name='customuser',
            name='user_id',
            field=models.UUIDField(null=True, blank=True),
        ),
        # Then populate it
        migrations.RunPython(gen_uuid),
        # Finally, make it unique and non-nullable
        migrations.AlterField(
            model_name='customuser',
            name='user_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]