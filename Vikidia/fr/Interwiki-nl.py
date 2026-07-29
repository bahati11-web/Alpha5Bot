import os
import warnings
warnings.filterwarnings("ignore")

os.environ["PYWIKIBOT_DIR"] = ""

import pywikibot
import re
import time

site = pywikibot.Site("fr", "vikidia")
wp_site = pywikibot.Site("fr", "wikipedia")
site.login()

print("- Connecté à Vikidia")

MAX_PAGES = 100
MAX_EDIT = 100

analysed = 0
edited = 0

def get_wikikids_title(wp_page):
    try:
        item = pywikibot.ItemPage.fromPage(wp_page)
        item.get()

        if "P12086" not in item.claims:
            return None

        return item.claims["P12086"][0].getTarget()

    except Exception:
        return None

for page in site.randompages(total=MAX_PAGES, namespaces=[0]):

    if edited >= MAX_EDIT:
        break

    analysed += 1
    title = page.title()

    try:
        if page.isRedirectPage():
            print(f"- {title} : redirection")
            continue

        text = page.text
        lower = text.lower()

        if "{{travaux" in lower:
            print(f"- {title} : travaux")
            continue

        if "{{homonymie" in lower:
            print(f"- {title} : homonymie")
            continue

        if re.search(r"\[\[nl:", text, re.I):
            print(f"- {title} : déjà lié")
            continue

        match = re.search(r"\[\[wp:([^\]|]+)", text, re.I)

        if not match:
            print(f"- {title} : pas de wp")
            continue

        wp_title = match.group(1).strip()

        wp_page = pywikibot.Page(wp_site, wp_title)

        if not wp_page.exists():
            print(f"- {title} : wp absent")
            continue

        wikikids = get_wikikids_title(wp_page)

        if not wikikids:
            print(f"- {title} : pas de WikiKids")
            continue

        link = f"[[nl:{wikikids}]]"

        if link in text:
            print(f"- {title} : déjà présent")
            continue

        page.text = text.rstrip() + "\n" + link

        page.save(
            summary=f"Ajout de {link}",
            minor=True,
            bot=True
        )

        edited += 1
        print(f"+ {title} ({edited}/{MAX_EDIT})")

        time.sleep(1)

    except Exception as e:
        print(f"! {title} : {e}")

print(f"\nTerminé : {edited} pages modifiées sur {analysed} analysées.")
