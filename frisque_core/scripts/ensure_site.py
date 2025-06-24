from django.contrib.sites.models import Site

def run():
    Site.objects.update_or_create(
        id=2,
        defaults={
            "domain": "frisque-web-app-46904927368.africa-south1.run.app",
            "name": "Frisque"
        }
    )
    print("✅ Site with ID=2 ensured.")
