import pywikibot
import re
import time

site = pywikibot.Site("fr", "vikidia")
site.login()

wp_site = pywikibot.Site("fr", "wikipedia")

MAX_MODIFIED = 100
modified_count = 0
BATCH_SIZE = 50

while modified_count < MAX_MODIFIED:
    print(f"\n===== Nouveau lot de {BATCH_SIZE} pages =====")

    random_pages = site.randompages(total=BATCH_SIZE, namespaces=[0])

    for page in random_pages:
        if modified_count >= MAX_MODIFIED:
            break

        print(f"\n=== Analyse : {page.title()} ===")

        try:
            if page.isRedirectPage():
                print("[SKIP] Redirection")
                continue

            text = page.text

            if "{{travaux" in text.lower():
                print("[SKIP] Modèle {{travaux}} détecté")
                continue

            if "[[simple:" in text.lower():
                print("[SKIP] Lien [[simple:]] déjà présent")
                continue

            if "{{homonymie" in text.lower():
                print("[SKIP] Page d'homonymie")
                continue

            match = re.search(r"\[\[wp:(.*?)\]\]", text)
            if not match:
                print("[SKIP] Aucun lien [[wp:]]")
                continue

            wp_title = match.group(1).strip()
            print(f"[INFO] Article Wikipédia : {wp_title}")

            wp_page = pywikibot.Page(wp_site, wp_title)

            if not wp_page.exists():
                print("[FAIL] Article Wikipédia inexistant")
                continue

            print("[INFO] Recherche de l'interwiki Simple...")

            simple_title = None
            for lang in wp_page.langlinks():
                if lang.site.code == "simple":
                    simple_title = lang.title
                    break

            if not simple_title:
                print("[FAIL] Aucun article sur Simple English")
                continue

            print(f"[OK] Interwiki trouvé : {simple_title}")

            simple_link = f"[[simple:{simple_title}]]"
            wp_link = f"[[wp:{wp_title}]]"

            if simple_link in text:
                print("[SKIP] Lien [[simple:]] déjà présent")
                continue

            print("[INFO] Préparation de la modification...")

            new_text = text.replace(
                wp_link,
                wp_link + "\n" + simple_link
            )

            page.text = new_text

            page.save(
                summary=f"Ajout de [[simple:{simple_title}]]",
                minor=True,
                bot=True
            )

            modified_count += 1
            print(f"[DONE] Ajout sur : {page.title()} ({modified_count}/{MAX_MODIFIED})")

            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] {page.title()} : {e}")

    time.sleep(1)

print(f"\n[INFO] Terminé : {modified_count} pages modifiées.")
