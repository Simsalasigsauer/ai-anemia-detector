from ultralytics import YOLO

model = YOLO("C:/Users/o2sti/Desktop/Forschungsprojekt/models/onlynails_anemiaplusfriends13/weights/best.pt")

source=r"C:\Users\o2sti\Desktop\Forschungsprojekt\Data\Test\Alisson.jpg"


results = model.predict(source, save=True, conf=0.3)
