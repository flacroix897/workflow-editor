from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workflow',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='workflow',
            old_name='diagram',
            new_name='contents',
        ),
    ]
