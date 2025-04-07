from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('base', '0005_delete_waterflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
    ]