import os
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def generate_synthetic_dataset(samples_per_class=500):
    """Generates synthetic training data based on EdgeGuard specifications."""
    np.random.seed(42)
    
    # Class 0: NORMAL
    temp_0 = np.random.normal(41.0, 3.0, samples_per_class)
    curr_0 = np.random.normal(0.85, 0.1, samples_per_class)
    vib_0 = np.random.normal(0.13, 0.05, samples_per_class)
    label_0 = np.zeros(samples_per_class)
    
    # Class 1: WARNING
    temp_1 = np.random.normal(64.0, 5.0, samples_per_class)
    curr_1 = np.random.normal(1.85, 0.3, samples_per_class)
    vib_1 = np.random.normal(0.48, 0.1, samples_per_class)
    label_1 = np.ones(samples_per_class)
    
    # Class 2: FAULT
    temp_2 = np.random.normal(91.0, 7.0, samples_per_class)
    curr_2 = np.random.normal(3.10, 0.4, samples_per_class)
    vib_2 = np.random.normal(1.10, 0.2, samples_per_class)
    label_2 = np.full(samples_per_class, 2)
    
    X = np.vstack([
        np.column_stack((temp_0, curr_0, vib_0)),
        np.column_stack((temp_1, curr_1, vib_1)),
        np.column_stack((temp_2, curr_2, vib_2))
    ])
    y = np.concatenate([label_0, label_1, label_2])
    
    return X, y

def main():
    print("Generating synthetic EdgeGuard dataset...")
    X, y = generate_synthetic_dataset()
    
    print("Splitting and Scaling data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Support Vector Machine (RBF Kernel)...")
    # probability=True is required for the confidence meter in the dashboard
    svm_model = SVC(kernel='rbf', probability=True, C=1.0, gamma='scale')
    svm_model.fit(X_train_scaled, y_train)
    
    print("Evaluating Model:")
    y_pred = svm_model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred, target_names=["NORMAL", "WARNING", "FAULT"]))
    
    print("Saving model and scaler to /models...")
    os.makedirs("models", exist_ok=True)
    joblib.dump(svm_model, "models/edgeguard_svm.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    print("Training complete. EdgeGuard ML Engine is ready.")

if __name__ == "__main__":
    main()