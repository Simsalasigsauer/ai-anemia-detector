import os
import ast
import pandas as pd

# === Bildgröße (in Pixel) ===
IMG_WIDTH = 800
IMG_HEIGHT = 600

# === Pfade anpassen ===
csv_path = r"C:\Users\Us\Desktop\Forschungsprojekt\Data\data\metadata.csv"
label_output_path = r"C:\Users\Us\Desktop\Forschungsprojekt\Data\data\labels"
os.makedirs(label_output_path, exist_ok=True)

# === CSV einlesen ===
df = pd.read_csv(csv_path)

# === Hilfsfunktion: YOLO-Format berechnen ===
def convert_box_to_yolo(x_min, y_min, x_max, y_max, img_w, img_h):
    x_center = (x_min + x_max) / 2.0 / img_w
    y_center = (y_min + y_max) / 2.0 / img_h
    width = (x_max - x_min) / img_w
    height = (y_max - y_min) / img_h
    return x_center, y_center, width, height

# === Durch alle Zeilen iterieren ===
for _, row in df.iterrows():
    # === Bildname aus erster Spalte (z. B. 1.jpg, 2.jpg, ...) ===
    img_id = str(row[0])  # Erste Spalte = Bildnummer
    txt_filename = f"{img_id}.txt"
    label_lines = []

    # === Haut-Bounding-Boxes (Klasse 0) ===
    skin_boxes = ast.literal_eval(row["SKIN_BOUNDING_BOXES"])
    for box in skin_boxes:
        x_min, y_min, x_max, y_max = box
        x, y, w, h = convert_box_to_yolo(x_min, y_min, x_max, y_max, IMG_WIDTH, IMG_HEIGHT)
        label_lines.append(f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}")

    # === Nagel-Bounding-Boxes (Klasse 1) ===
    nail_boxes = ast.literal_eval(row["NAIL_BOUNDING_BOXES"])
    for box in nail_boxes:
        x_min, y_min, x_max, y_max = box
        x, y, w, h = convert_box_to_yolo(x_min, y_min, x_max, y_max, IMG_WIDTH, IMG_HEIGHT)
        label_lines.append(f"1 {x:.6f} {y:.6f} {w:.6f} {h:.6f}")

    # === Datei schreiben ===
    with open(os.path.join(label_output_path, txt_filename), "w") as f:
        f.write("\n".join(label_lines))

print("✅ YOLO-Annotationen für alle Bilder erfolgreich erstellt.")
