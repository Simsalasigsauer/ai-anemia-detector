import shutil
import os

# Diese Ordner sollen gelöscht werden
dirs_to_delete = [
    r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\images\train",
    r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\images\val",
    r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\labels\train",
    r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\labels\val"
]

for path in dirs_to_delete:
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Gelöscht: {path}")
    else:
        print(f"Nicht gefunden: {path}")

from sklearn.model_selection import train_test_split
import os
import shutil

# === Basispfade ===
base_image_path = r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\photoblanco"
base_label_path = r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\labelsblanco"

output_image = r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\images"
output_label = r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\data\labels"

# === Kategorien
categories = ["anemiahands", "friendshands"]

# === Funktion
def split_and_copy(category):
    image_dir = os.path.join(base_image_path, category)
    label_dir = os.path.join(base_label_path, category)

    filenames = [f for f in os.listdir(image_dir) if f.lower().endswith((".jpg", ".png"))]

    train_files, val_files = train_test_split(filenames, test_size=0.2, random_state=42)

    for split_name, filelist in [("train", train_files), ("val", val_files)]:
        dst_img = os.path.join(output_image, split_name)
        dst_lbl = os.path.join(output_label, split_name)
        os.makedirs(dst_img, exist_ok=True)
        os.makedirs(dst_lbl, exist_ok=True)

        for fname in filelist:
            src_img = os.path.join(image_dir, fname)
            src_lbl = os.path.join(label_dir, fname.rsplit(".", 1)[0] + ".txt")

            # Konvertiere PNG nach JPG wenn nötig
            if fname.lower().endswith(".png"):
                import cv2
                img = cv2.imread(src_img)
                new_name = fname.replace(".png", ".jpg")
                new_path = os.path.join(dst_img, new_name)
                cv2.imwrite(new_path, img)
                fname = new_name
            else:
                shutil.copy(src_img, os.path.join(dst_img, fname))

            # Label kopieren
            if os.path.exists(src_lbl):
                shutil.copy(src_lbl, os.path.join(dst_lbl, fname.replace(".jpg", ".txt")))

    print(f"{category}: {len(train_files)} train, {len(val_files)} val")

# === Hauptaufruf
for cat in categories:
    split_and_copy(cat)
