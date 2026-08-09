from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
JSON_FILE = ROOT / "jsons" / "Nations.json"
BACKUP = ROOT / "jsons" / "Nations.json.backup"

print("=== Star Wars Nations - réparateur Unciv 4.21.2 ===")
print()

if not JSON_FILE.exists():
    print("ERREUR : jsons/Nations.json est introuvable.")
    input("Appuie sur Entrée pour fermer...")
    raise SystemExit(1)

# Sauvegarde
if not BACKUP.exists():
    shutil.copy2(JSON_FILE, BACKUP)
    print("Sauvegarde créée :", BACKUP.name)

text = JSON_FILE.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Réparer les propriétés JSON séparées par une ligne
#    sans virgule.
#
# Exemple :
#   "defeated": "..."
#   "outerColor": [...]
#
# devient :
#   "defeated": "...",
#   "outerColor": [...]
# ------------------------------------------------------------

lines = text.splitlines()

fixed = []
repairs = 0

property_re = re.compile(r'^\s*"[^"]+"\s*:\s*')

for i, line in enumerate(lines):
    stripped = line.rstrip()

    if fixed:
        previous = fixed[-1].rstrip()

        # Deux propriétés consécutives dans le même objet.
        if (
            property_re.match(previous)
            and property_re.match(stripped)
            and not previous.endswith((",", "{", "["))
        ):
            fixed[-1] = previous + ","
            repairs += 1

        # Une propriété suivie d'une fermeture d'objet.
        if (
            property_re.match(previous)
            and stripped.startswith("}")
            and not previous.endswith((",", "{", "["))
        ):
            fixed[-1] = previous + ","
            repairs += 1

    fixed.append(line)

text = "\n".join(fixed) + "\n"

# ------------------------------------------------------------
# 2. Corriger les anciennes appellations de terrains.
# ------------------------------------------------------------

replacements = {
    '"Grasslands"': '"Grassland"',
    '"Hills"': '"Hill"',
    '"Avoid Grasslands"': '"Avoid Grassland"',
}

for old, new in replacements.items():
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        print(f"Terrain corrigé : {old} -> {new} ({count} occurrence(s))")

# "None" n'est pas un startBias utile : on le supprime.
text = re.sub(
    r'"startBias"\s*:\s*\[\s*"None"\s*\]',
    '"startBias": []',
    text
)

# ------------------------------------------------------------
# 3. Normaliser les types de cités-États.
# ------------------------------------------------------------

city_state_types = {
    '"cultured"': '"Cultured"',
    '"maritime"': '"Maritime"',
    '"mercantile"': '"Mercantile"',
    '"militaristic"': '"Militaristic"',
    '"religious"': '"Religious"',
    '"Industrial"': '"Mercantile"',
}

for old, new in city_state_types.items():
    count = text.count('"cityStateType": ' + old)
    if count:
        text = text.replace(
            '"cityStateType": ' + old,
            '"cityStateType": ' + new
        )
        print(f"Type CS normalisé : {old} -> {new} ({count})")

# ------------------------------------------------------------
# 4. Sauvegarder le fichier réparé.
# ------------------------------------------------------------

JSON_FILE.write_text(text, encoding="utf-8")

print()
print(f"Corrections syntaxiques effectuées : {repairs}")
print()

# ------------------------------------------------------------
# 5. Vérification JSON stricte.
# ------------------------------------------------------------

try:
    data = json.loads(text)

    if not isinstance(data, list):
        raise ValueError("Nations.json ne contient pas une liste JSON.")

    print("OK : Nations.json est maintenant un JSON valide.")
    print(f"Entrées détectées : {len(data)}")

except json.JSONDecodeError as e:
    print("ATTENTION : le fichier contient encore une erreur JSON.")
    print()
    print(f"Ligne : {e.lineno}")
    print(f"Colonne : {e.colno}")
    print(f"Erreur : {e.msg}")
    print()
    print("La sauvegarde originale est conservée dans :")
    print(BACKUP)
    print()
    print("Ne supprime pas cette sauvegarde.")

except Exception as e:
    print("ATTENTION :", e)

print()
input("Appuie sur Entrée pour fermer...")