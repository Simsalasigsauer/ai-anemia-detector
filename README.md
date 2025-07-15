# Non-Invasive Hemoglobin Prediction using AI

![Project Banner](https://github.com/Simsalasigsauer/ai-anemia-detector/blob/main/assets/banner.JPG)  

An end-to-end web application to estimate hemoglobin (Hb) levels non-invasively from fingernail images. This project uses a two-stage computer vision and machine learning pipeline to provide a fast, accessible, and painless alternative to traditional blood tests for anemia screening.

## Table of Contents
- [Project Vision](#project-vision)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [AI Pipeline Explained](#ai-pipeline-explained)
  - [Stage 1: Fingernail Detection (YOLOv8)](#stage-1-fingernail-detection-yolov8)
  - [Stage 2: Hemoglobin Regression](#stage-2-hemoglobin-regression)
- [Results](#results)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
- [Usage](#usage)
  - [1. Data Preparation](#1-data-preparation)
  - [2. Model Training](#2-model-training)
  - [3. Running the Web Application](#3-running-the-web-application)
- [Future Work](#future-work)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Project Vision

Anemia, a condition caused by a lack of hemoglobin, affects billions of people worldwide. Standard diagnosis requires invasive blood tests, which are often inconvenient, costly, and inaccessible in resource-limited regions. This project aims to solve this problem by developing an AI-powered system that can accurately estimate a person's Hb value from a simple smartphone photo of their fingernails.

The goal is to create a tool that empowers at-risk individuals (e.g., pregnant women, chronically ill patients) for self-monitoring and provides healthcare professionals with a new, efficient monitoring method, especially in areas with poor laboratory infrastructure.

## Key Features

- **Non-Invasive Analysis**: Predicts Hb levels using only a fingernail image.
- **Two-Stage AI Pipeline**: Combines a high-precision object detection model with a robust regression model.
- **Interactive Web Application**: User-friendly interface for capturing images, viewing predictions, and managing user data.
- **Secure User Management**: Features user registration, login, and secure data handling with JWT authentication.
- **Data Visualization**: Presents the predicted Hb value in a clear and understandable way.

## Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **Machine Learning**: Scikit-learn, PyTorch, Ultralytics (YOLOv8)
- **Data Handling**: Pandas, NumPy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: MongoDB Atlas
- **Deployment (Planned)**: Docker, AWS (S3, EC2)

## System Architecture

The application is built on a client-server architecture. The **Flask backend** serves a REST-API that handles user authentication, data storage, and executes the AI pipeline. The **vanilla JS frontend** communicates with the API to provide an interactive user experience.



## AI Pipeline Explained

### Stage 1: Fingernail Detection (YOLOv8)
The first step is to automatically locate the relevant regions of interest (ROIs) – the fingernails.
- **Model**: A custom-trained **YOLOv8** object detection model.
- **Training Data**: Trained on a diverse dataset of ~450 hand images, including the public "Shirshin et al., 2024" dataset and custom photos taken under various lighting conditions and with different smartphone cameras.
- **Performance**: Achieved a **mAP50 of 0.972**, meaning it correctly localizes 97.2% of fingernails with high precision.

### Stage 2: Hemoglobin Regression
Once the fingernails are detected, their color features are used to predict the Hb value.
- **Feature Extraction**: The average Red, Green, and Blue (RGB) values are calculated across all detected fingernails for a given user.
- **Normalization**: A white-balance normalization technique is applied to minimize the impact of varying lighting conditions.
- **Model Comparison**: Various classical ML models were evaluated. A **Gradient Boosting Regressor** proved to be the most performant model for predicting the numerical Hb value (in g/L).

## Results

The final Gradient Boosting model achieved the following performance on the test set:
| Metric | Value |
| :--- | :--- |
| **Mean Absolute Error (MAE)** | **16.41 g/L** |
| Root Mean Squared Error (RMSE) | 20.97 g/L |
| R² Score | 0.37 |

While the current accuracy is not yet sufficient for clinical diagnosis, it provides a solid foundation and demonstrates the feasibility of the approach.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- Git
- An account on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (for the database)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai-anemia-detector.git
    cd ai-anemia-detector
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory and add your MongoDB connection string and a secret key:
    ```
    MONGO_URI="your_mongodb_atlas_connection_string"
    SECRET_KEY="a_very_strong_and_random_secret_key"
    ```

## Usage

### 1. Data Preparation
Place your raw image data in the `data/raw/` directory and your metadata (e.g., CSV with Hb values) as well. Run the data preparation scripts to process the data and create features.
```bash

python src/data_processing/prepare_data.py
```

### 2. Model Training
To train the regression and detection models from scratch:
```bash
# Train the YOLOv8 model for nail detection
python src/model_training/train_yolo.py

# Train the Hb value regression model
python src/model_training/train_regressor.py
```
This will save the best models (`best.pt` and `best_regressor.pkl`) to the `models/` directory.

### 3. Running the Web Application
Start the Flask development server:
```bash
python src/app/main.py
```
Open your web browser and navigate to `http://127.0.0.1:5000`.

## Future Work

- [ ] **Improve Accuracy**: Integrate a larger, clinically validated dataset and explore advanced features (e.g., HSV/Lab color spaces, texture analysis).
- [ ] **End-to-End Deep Learning**: Develop a CNN-based regression model that learns directly from the nail crops, potentially identifying more subtle biomarkers.
- [ ] **Dockerize the Application**: Create Dockerfiles for the frontend and backend to simplify deployment.
- [ ] **Deploy to the Cloud**: Deploy the application on AWS using services like S3 for data storage and EC2/Fargate for hosting.
- [ ] **Mobile-First Porting**: Port the models to TFLite or ONNX to enable a fully offline, privacy-friendly mobile app.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- This project utilizes the dataset provided by **Shirshin, E. A., et al.** (2024) in *Dataset of human skin and fingernails images for non-invasive haemoglobin level assessment*.
- Gratitude to the open-source community for tools like `scikit-learn`, `PyTorch`, and `Flask`.