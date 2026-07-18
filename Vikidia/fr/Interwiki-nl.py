import os
#
import pywikibot
import re
import time

site=pywikibot.Site("fr","vikidia")
wp_site=pywikibot.Site("fr","wikipedia")
site.login()

print("[OK] Connecté")

MAX_MODIFIED=100
modified_count=0
BATCH_SIZE=50

def get_wikikids_title(wp_page):
    try:
        item=pywikibot.ItemPage.fromPage(wp_page)
        item.get()
        if "P12086" not in item.claims:
            return None
        return item.claims["P12086"][0].getTarget()
    except Exception as e:
        print("[ERROR] Wikidata :",e)
        return None

while modified_count<MAX_MODIFIED:
    print(f"\n===== Lot de {BATCH_SIZE} pages =====")

    for page in site.randompages(total=BATCH_SIZE,namespaces=[0]):
        if modified_count>=MAX_MODIFIED:
            break

        print(f"\n=== {page.title()} ===")

        try:
            if page.isRedirectPage():
                print("[SKIP] Redirection")
                continue

            text=page.text

            if "{{travaux" in text.lower():
                print("[SKIP] Travaux")
                continue

            if "{{homonymie" in text.lower():
                print("[SKIP] Homonymie")
                continue

            if re.search(r"\[\[nl:",text,re.I):
                print("[SKIP] nl déjà présent")
                continue

            match=re.search(r"\[\[wp:([^\]|]+)",text,re.I)
            if not match:
                print("[SKIP] Pas de wp")
                continue

            wp_title=match.group(1).strip()
            print("[INFO] WP :",wp_title)

            wp_page=pywikibot.Page(wp_site,wp_title)

            if not wp_page.exists():
                print("[FAIL] WP absent")
                continue

            print("[INFO] Wikidata...")

            wikikids=get_wikikids_title(wp_page)

            if not wikikids:
                print("[SKIP] Pas de WikiKids")
                continue

            print("[OK] WikiKids :",wikikids)

            link=f"[[nl:{wikikids}]]"

            if link in text:
                print("[SKIP] Déjà présent")
                continue

            page.text=text.rstrip()+"\n"+link

            page.save(
                summary=f"Ajout de {link}",
                minor=True,
                bot=True
            )

            modified_count+=1
            print(f"[DONE] {page.title()} ({modified_count}/{MAX_MODIFIED})")

            time.sleep(2)

        except Exception as e:
            print("[ERROR]",page.title(),":",e)

    time.sleep(3)

print(f"\n[FIN] {modified_count} modifications")
