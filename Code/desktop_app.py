import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtCore import Qt
from ultralytics import YOLO
import cv2
import math
import subprocess

models = {
    "E:/Research_Papers/Nahid sir/Faisal Vai/Model/yolov8n_best.pt": "Nano",
    "E:/Research_Papers/Nahid sir/Faisal Vai/Model/yolov8s_best.pt": "Small",
    "E:/Research_Papers/Nahid sir/Faisal Vai/Model/yolov8m_best.pt": "Medium",
    "E:/Research_Papers/Nahid sir/Faisal Vai/Model/yolov8l_best.pt": "Large",
    "E:/Research_Papers/Nahid sir/Faisal Vai/Model/yolov8x_best.pt": "X_Large"
}

classNames = ['']  # Update this if different models have different class names
min_confidence = 0.5
desired_resolution = (256, 256)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the fixed size of the window to 1200x720
        self.setFixedSize(1280, 700)
        # Main layout
        mainLayout = QVBoxLayout()
        # App name label
        # App name label
        appNameLabel = QLabel('Polyp Localization & Segmentation')
        appNameLabel.setAlignment(Qt.AlignCenter)
        appNameLabel.setFont(QFont('Georgia', 30))
        appNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        appNameLabel.setFixedHeight(50)  # Set fixed height for the app name label
        appNameLabel.setStyleSheet("""
    background-color: #f2ee9b;
    border-style: solid;
    border-radius: 5px;
    border-width: 2px;
    border-color: black;
""")



        # Add the app name label to the main layout
        mainLayout.addWidget(appNameLabel)

        # Create the top layout with buttons
        self.topLayout = QHBoxLayout()

        # Create and add Button 1
        button1 = QPushButton('Localization')
        self.styleButtons(button1)
        self.topLayout.addWidget(button1)
        button1.setFixedHeight(48) 
        button1.setFixedWidth(400) 
        button1.setFont(QFont('Georgia', 25))

        # Create and add Button 2
        button2 = QPushButton('Segmentation')
        self.styleButtons(button2)
        self.topLayout.addWidget(button2)
        button2.setFixedHeight(48) 
        button2.setFixedWidth(400) 
        button2.setFont(QFont('Georgia', 25))

        # Create and add Button 3
        # button3 = QPushButton('In Shaa Allah')
        # self.styleButtons(button3)
        # self.topLayout.addWidget(button3)
        # Top container
        topContainer = QWidget()
        topContainer.setLayout(self.topLayout)
        topContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        topContainer.setFixedHeight(70)  # Set fixed height for the top layout container
        mainLayout.addWidget(topContainer)

        # Bottom layout
        self.bottomLayout = QVBoxLayout()

        # Create rows of image labels
        # ... (inside your initUI method)

# Create rows of image labels
        row1Layout, row2Layout = QHBoxLayout(), QHBoxLayout()
        for i in range(6):
            label = QLabel(f'Image {i+1}')
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: #dbd5ed; border: 1px solid black;")
            container = self.createImageContainer(label)
            if i < 3:
                row1Layout.addWidget(container)
            else:
                row2Layout.addWidget(container)

            # Assign labels as attributes
            setattr(self, f'imageLabel{i+1}', label)

# ...


        # Add the rows to the bottom layout
        self.bottomLayout.addLayout(row1Layout)
        self.bottomLayout.addLayout(row2Layout)

        # Bottom container
        bottomContainer = QWidget()
        bottomContainer.setLayout(self.bottomLayout)
        bottomContainer.setStyleSheet("background-color: #39383b;")
        mainLayout.addWidget(bottomContainer)

        # Set the main layout of the window
        self.setLayout(mainLayout)

        # Set background image
        # self.setStyleSheet("QWidget { background-image: url('E:/Research_Papers/Nahid sir/Faisal Vai/Code/bg.jpg'); }")

        # Connect the button click to openImage method
        button1.clicked.connect(self.openImage)
        button2.clicked.connect(self.segmentImage)

        self.setWindowTitle('Polyp Localization & Segmentation')
        self.show()

    def createImageContainer(self, imageLabel):
        """Create a container for an image label."""
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(imageLabel)
        container.setLayout(layout)
        return container

    def styleButtons(self, button):
        """Style the buttons with increased height and font size."""
        button.setFixedHeight(40)
        button.setFont(QFont('Arial', 12))

    def openImage(self):
    # Open a file dialog to select an image
        imagePath, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)')
        if imagePath:
            # pixmap = QPixmap(imagePath)
            img = cv2.imread(imagePath)
            img = cv2.resize(img, desired_resolution)
            i=2
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_Qt_format)
            
            label = getattr(self, f'imageLabel{1}')
            label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            for model_file, model_name in models.items():
                print(f"Processing with model: {model_name}")
                # Load the model
                model = YOLO(model_file)
                # Perform detection
                results = model(img)
                # Process results
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        confidence = math.ceil((box.conf[0]*100))/100
                        if confidence >= min_confidence:
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                            cls = int(box.cls[0])
                            print("Class name -->", classNames[cls])
                            org = (x1+1, y1-3)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = .6
                            color = (10, 10, 10)
                            thickness = 2
                            cv2.putText(img, f"{model_name}: {confidence:.2f}", org, font, fontScale, color, thickness)
            # Set the image in all image labels individually
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(convert_to_Qt_format)
                label = getattr(self, f'imageLabel{i}')
                label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                i=i+1
                img = cv2.imread(imagePath)
                img = cv2.resize(img, desired_resolution)
                
    def segmentImage(self):
        subprocess.run(['python', 'E:/Research_Papers/Nahid sir/Faisal Vai/Code/main_2.py'])

# self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

