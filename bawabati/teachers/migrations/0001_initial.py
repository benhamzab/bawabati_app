# Generated by Django 5.2 on 2025-05-15 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Professeur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('prenom', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=192, unique=True)),
                ('matiere', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
