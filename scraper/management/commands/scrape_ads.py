# scraper/management/commands/scrape_ads.py

import cloudscraper  # helps bypass Cloudflare if needed
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from scraper.models import ClassifiedAd

class Command(BaseCommand):
    help = "Scrape classified gun ads from caguns.net for NORCAL ads using updated selectors"

    def handle(self, *args, **options):
        url = "https://caguns.net/classifieds/?filter=norcal&sort=create_date"
        self.stdout.write(f"Fetching {url}...")

        # Use cloudscraper to handle potential Cloudflare protections.
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        self.stdout.write(f"Response status: {response.status_code}")
        if response.status_code != 200:
            self.stdout.write("Error fetching the site")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Find the main container holding the gun ads.
        container = soup.find("div", class_="structItemContainerCasListView")
        if not container:
            self.stdout.write("No ad container found")
            return

        ads_found = 0
        # Find all ad items within the container. We use a lambda to match classes containing "structItem--ad".
        ad_items = container.find_all("div", class_=lambda value: value and "structItem--ad" in value)
        for ad in ad_items:
            # Within each ad, find the cell that contains the main information.
            main_cell = ad.find("div", class_="structItem-cell--main")
            if not main_cell:
                continue

            # Extract the title.
            title_div = main_cell.find("div", class_="structItem-title")
            title = title_div.get_text(strip=True) if title_div else "No Title"
            # Usually the title contains a link.
            link_tag = title_div.find("a", href=True) if title_div else None
            link = link_tag["href"] if link_tag else None

            # Extract the description.
            # description_div = main_cell.find("div", class_="structItem-adDescription")
            # description = description_div.get_text(strip=True) if description_div else ""

            # Extract the price.
            price_div = main_cell.find("div", class_="structItem-adPrice")
            price = price_div.get_text(strip=True) if price_div else ""

            # Only add the ad if we have a valid link and it isn't already in the database.
            if link and not ClassifiedAd.objects.filter(link=link).exists():
                ClassifiedAd.objects.create(
                    title=title,
                    price=price,
                    # description=description,l
                    link=link
                )
                ads_found += 1
                self.stdout.write(f"Added ad: {title}")

        self.stdout.write(f"Scraping complete. {ads_found} new ad(s) added.")
