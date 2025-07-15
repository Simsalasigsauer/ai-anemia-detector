from ultralytics import YOLO

def main():
    model = YOLO("yolov8x.pt")  # alternativ yolov8n.pt, yolov8s.pt, ...

    model.train(
        data="data.yaml",                         # dein Datenpfad
        epochs=50,
        imgsz=800,
        batch=8,
        name="onlynailsplusinkfriends",                            
        project="D:/Forschungsprojekt/models"                     
    )

if __name__ == "__main__":
    main()
