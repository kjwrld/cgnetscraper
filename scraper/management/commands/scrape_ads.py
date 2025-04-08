# scraper/management/commands/scrape_ads.py

import time
from urllib.parse import urlencode, urljoin
import cloudscraper
from dateutil.parser import parse as parse_datetime
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from scraper.models import ClassifiedAd
from scraper.utils import send_text_notification
class Command(BaseCommand):
    help = "Scrape classified gun ads from caguns.net for NORCAL ads using updated selectors."

    def add_arguments(self, parser):
        # Flag to control text notifications.
        parser.add_argument(
            "--notify",
            action="store_true",
            help="Send text notifications when new ads are scraped."
        )
        # Flag for the number of pages to scrape.
        parser.add_argument(
            "--pages",
            type=int,
            default=15,
            help="Number of pages to scrape (default: 10)"
        )

    def handle(self, *args, **options):
        notify = options.get("notify", False)
        max_pages = options.get("pages", 15)
        base_url = "https://caguns.net"
        ads_found = 0
        new_ads_messages = []

        # Create the cloudscraper scraper to handle potential Cloudflare protections.
        scraper = cloudscraper.create_scraper()

        # Loop over each page.
        for page in range(1, max_pages + 1):
            # Build URL with appropriate query parameters.
            params = {
                "filter": "norcal",
                "sort": "create_date",
                "page": page
            }
            url = f"{base_url}/classifieds/?{urlencode(params)}"
            self.stdout.write(f"\nFetching page {page}: {url}...")
            
            response = scraper.get(url)
            self.stdout.write(f"Response status: {response.status_code}")

            if response.status_code != 200:
                self.stdout.write(f"Error fetching page {page}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Locate the container that holds all the listings.
            container = soup.find("div", class_=lambda x: x and "structItemContainerCasListView" in x)
            if not container:
                self.stdout.write("Could not find the ad container on this page")
                continue
            else:
                count = len(container.find_all("div", class_=lambda x: x and "structItem--ad" in x))
                self.stdout.write(f"Found {count} ad element(s) on page {page}")

            # Iterate over all individual ad containers.
            for ad in container.find_all("div", class_=lambda x: x and "structItem--ad" in x):
                cell = ad.find("div", class_="structItem-cell structItem-cell--main structItem-cell--listViewLayout")
                if not cell:
                    self.stdout.write("Cell not found; skipping ad.")
                    continue

                # --- REGION & SUB-REGION EXTRACTION ---
                region = ""
                sub_region = ""
                custom_fields_div = cell.find("div", class_="structItem-adCustomFields")
                if custom_fields_div:
                    fields_div = custom_fields_div.find("div", class_=lambda x: x and "listViewLayout-fields" in x)
                    if fields_div:
                        region_dl = fields_div.find("dl", {"data-field": "region"})
                        sub_region_dl = fields_div.find("dl", {"data-field": "sub_region"})
                        if region_dl:
                            region_dd = region_dl.find("dd")
                            if region_dd:
                                region = region_dd.get_text(strip=True)
                        if sub_region_dl:
                            sub_region_dd = sub_region_dl.find("dd")
                            if sub_region_dd:
                                sub_region = sub_region_dd.get_text(strip=True)

                # Only proceed if region is "NorCal" and sub_region is "Bay Area".
                if region.lower() != "norcal" or sub_region.lower() != "bay area":
                    self.stdout.write(f"Ad skipped due to region mismatch: region='{region}', sub_region='{sub_region}'")
                    continue

                # --- TITLE & LINK EXTRACTION ---
                title_div = cell.find("div", class_="structItem-title")
                title = ""
                link = ""
                if title_div:
                    a_tags = title_div.find_all("a")
                    # Usually, the first <a> is the label and the second contains the actual title.
                    if len(a_tags) >= 2:
                        title_a = a_tags[1]
                    elif a_tags:
                        title_a = a_tags[0]
                    else:
                        title_a = None

                    if title_a:
                        title = title_a.get_text(strip=True)
                        relative_link = title_a.get("href", "")
                        link = urljoin(base_url, relative_link)
                    else:
                        self.stdout.write("Title anchor not found for an ad.")
                else:
                    self.stdout.write("Title container not found for an ad.")

                # --- DESCRIPTION EXTRACTION ---
                desc_tag = cell.find("div", class_="structItem-adDescription")
                description = desc_tag.get_text(strip=True) if desc_tag else ""

                # --- PRICE EXTRACTION ---
                price_tag = cell.find("div", class_="structItem-adPrice")
                price = price_tag.get_text(strip=True) if price_tag else ""
                
                # --- DATE EXTRACTION ---
                # Extract the posted date (created date) from the createdate element.
                posted_at = None
                created_dl = cell.find("dl", class_=lambda x: x and "structItem-metaItem--createdate" in x)
                if created_dl:
                    time_tag = created_dl.find("time", class_="u-dt")
                    if time_tag and time_tag.has_attr("datetime"):
                        try:
                            posted_at = parse_datetime(time_tag["datetime"])
                        except Exception as e:
                            self.stdout.write(f"Error parsing posted_at: {e}")

                # Extract the updated date from the lastUpdate element.
                updated_at = None
                update_dl = cell.find("dl", class_=lambda x: x and "structItem-metaItem--lastUpdate" in x)
                if update_dl:
                    time_tag = update_dl.find("time", class_="u-dt")
                    if time_tag and time_tag.has_attr("datetime"):
                        try:
                            updated_at = parse_datetime(time_tag["datetime"])
                        except Exception as e:
                            self.stdout.write(f"Error parsing updated_at: {e}")

                self.stdout.write(f"Extracted: title='{title}', price='{price}', link='{link}', posted_at='{posted_at}', updated_at='{updated_at}'")

                # Only create the ad if title and link were successfully extracted.
                if title and link:
                    # need to check link for https://caguns.net/classifieds/?prefix_id
                    if not ClassifiedAd.objects.filter(link=link).exists():
                        ClassifiedAd.objects.create(
                            title=title,
                            description=description,
                            price=price,
                            link=link
                        )
                        ads_found += 1
                        self.stdout.write(f"Added ad: {title}")

                        new_ads_messages.append(f"Title: {title}\nPrice: {price}\nLink: {link}\n")
                    else:
                        self.stdout.write(f"Ad already exists: {title}")
                else:
                    self.stdout.write("Incomplete data; ad skipped.")

            # Pause between pages to avoid overwhelming the server.
            time.sleep(1)

        # waiting for twilio clearance
        if notify and new_ads_messages:
            message_body = "New Classified Ad Alerts:\n\n" + "\n".join(new_ads_messages)
            send_text_notification(message_body)
            self.stdout.write("Sent consolidated text notification.")

        self.stdout.write(f"\nScraping complete. {ads_found} new ad(s) added.")
