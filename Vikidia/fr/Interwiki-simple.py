import os
import warnings
warnings.filterwarnings("ignore")

os.environ["PYWIKIBOT_DIR"] = ""

import pywikibot
import re
import time

site = pywikibot.Site("fr", "vikidia")
site.login()

wp_site = pywikibot.Site("fr", "wikipedia")

print("- Connecté à Vikidia")

MAX_PAGES = 100 
MAX_EDIT = 100   

analysed = 0
edited = 0

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

        if "[[simple:" in lower:
            print(f"- {title} : déjà lié")
            continue

        match = re.search(r"\[\[wp:([^\]|]+)", text, re.IGNORECASE)

        if not match:
            print(f"- {title} : pas de wp")
            continue

        wp_title = match.group(1).strip()

        wp_page = pywikibot.Page(wp_site, wp_title)

        if not wp_page.exists():
            print(f"- {title} : wp absent")
            continue
            
        simple_title = None

        for lang in wp_page.langlinks():
            if lang.site.code == "simple":
                simple_title = lang.title
                break

        if not simple_title:
            print(f"- {title} : pas de simple")
            continue

        wp_link = f"[[wp:{wp_title}]]"
        simple_link = f"[[simple:{simple_title}]]"

        new_text = text.replace(wp_link, wp_link + "\n" + simple_link, 1)

        if new_text == text:
            print(f"- {title} : aucune modif")
            continue

        page.text = new_text
        page.save(
            summary=f"Ajout de [[simple:{simple_title}]]",
            minor=True,
            bot=True
        )

        edited += 1
        print(f"+ {title} ({edited}/{MAX_EDIT})")

        time.sleep(0.5)

    except Exception as e:
        print(f"! {title} : {e}")
print(f"\nTerminé : {edited} pages modifiées sur {analysed} analysées.")
