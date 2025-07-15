import os
import shutil
import pandas as pd

# === 1. Pfade anpassen ===
original_dir = r"C:\Users\Us\iCloudDrive\Master\2.Semester\Forschungsprojekt\Data\data\photo"   # z. B. r"C:\Users\Us\Downloads\original_images"
output_dir = r"C:\Users\Us\iCloudDrive\Master\2.Semester\Forschungsprojekt\Data\data\richtigsortiert"        # z. B. r"C:\Users\Us\Downloads\renamed_images"

# === 2. Erstelle Zielordner, falls er nicht existiert ===
os.makedirs(output_dir, exist_ok=True)

# === 3. Liste der Originaldateien holen und sortieren ===
original_files = sorted(os.listdir(original_dir))  # Alphabetisch sortiert
mapping = []

# === 4. Dateien kopieren und umbenennen ===
for index, orig_name in enumerate(original_files, start=1):
    orig_path = os.path.join(original_dir, orig_name)

    # Neue Namen als JPG (oder passe das bei Bedarf an, z. B. .png)
    new_name = f"{index}.jpg"
    new_path = os.path.join(output_dir, new_name)

    # Kopieren & Zuordnung speichern
    shutil.copyfile(orig_path, new_path)
    mapping.append((new_name, orig_name))

# === 5. Mapping als CSV speichern ===
df = pd.DataFrame(mapping, columns=["renamed_file", "original_file"])
df.to_csv("bild_mapping.csv", index=False)

print("✅ Alle Bilder wurden neu durchnummeriert kopiert und Mapping gespeichert als 'bild_mapping.csv'.")
