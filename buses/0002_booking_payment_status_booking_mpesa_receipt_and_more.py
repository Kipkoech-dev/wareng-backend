from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('buses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='mpesa_receipt',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='checkout_request_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
