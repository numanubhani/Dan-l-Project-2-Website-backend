# Data migration: create BetMarkerOption for existing BetMarkers that only have option1/option2

from django.db import migrations


def populate_bet_marker_options(apps, schema_editor):
    BetMarker = apps.get_model('accounts', 'BetMarker')
    BetMarkerOption = apps.get_model('accounts', 'BetMarkerOption')
    for marker in BetMarker.objects.all():
        if BetMarkerOption.objects.filter(marker=marker).exists():
            continue
        if marker.option1_text or marker.option2_text:
            BetMarkerOption.objects.create(
                marker=marker,
                text=marker.option1_text or 'Yes',
                odds=marker.option1_odds,
                order=0,
            )
            BetMarkerOption.objects.create(
                marker=marker,
                text=marker.option2_text or 'No',
                odds=marker.option2_odds,
                order=1,
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_betting_and_notifications'),
    ]

    operations = [
        migrations.RunPython(populate_bet_marker_options, noop),
    ]
