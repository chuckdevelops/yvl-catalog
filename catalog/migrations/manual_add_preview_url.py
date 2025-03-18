from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0014_recommendationinsights'),
    ]

    operations = [
        migrations.AddField(
            model_name='carticatalog',
            name='preview_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]