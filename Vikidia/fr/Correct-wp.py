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

PATTERN = re.compile(
    r"\[\[wp:\s*\{\{(?:PAGENAME|FULLPAGENAME)\}\}\s*(?:\|[^\]]*)?\]\]",
    re.I
)

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

        match = PATTERN.search(text)

        if not match:
            print(f"- {title} : pas de modèle dans wp")
            continue

        wp_page = pywikibot.Page(wp_site, title)

        if wp_page.exists():

            replacement = f"[[wp:{title}]]"

            new_text = PATTERN.sub(replacement, text)

            if new_text == text:
                print(f"- {title} : aucune modification")
                continue

            page.text = new_text

            page.save(
                summary="Correction du lien [[wp:]]",
                minor=True,
                bot=True
            )

            edited += 1
            print(f"+ {title} : corrigé ({edited}/{MAX_EDIT})")

        else:

            new_text = PATTERN.sub("", text)
            new_text = re.sub(r"[ \t]{2,}", " ", new_text)
            new_text = re.sub(r"\n{3,}", "\n\n", new_text)

            if new_text == text:
                print(f"- {title} : rien à supprimer")
                continue

            page.text = new_text

            page.save(
                summary="Correction du lien [[wp:]]",
                minor=True,
                bot=True
            )

            edited += 1
            print(f"+ {title} : lien supprimé ({edited}/{MAX_EDIT})")

        time.sleep(1)

    except Exception as e:
        print(f"! {title} : {e}")

print(f"\nTerminé : {edited} pages modifiées sur {analysed} analysées.")
