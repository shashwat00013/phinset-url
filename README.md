# Phishing URL Detector

An AI-powered web application that analyzes URLs to detect potential phishing attempts using machine learning and heuristic rules.

## 🚀 Features

- **Real-time URL Analysis**: Instant detection of malicious URLs
- **Machine Learning Model**: Trained on large datasets using TF-IDF and structural features
- **Heuristic Rules**: Additional safety checks for known trusted/risky domains
- **Web Interface**: Clean, responsive UI built with Tailwind CSS
- **REST API**: Backend API for programmatic access
- **High Accuracy**: Combines ML predictions with rule-based adjustments

## 📊 Model Performance

The model achieves high accuracy on phishing detection with:
- Character-level TF-IDF vectorization (3-5 grams)
- Structural URL features (length, special characters, domain analysis)
- Logistic regression classifier with balanced class weights
- Heuristic adjustments for known safe/risky domains

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **ML**: Scikit-learn, Pandas, NumPy
- **Features**: Custom URL feature extraction
- **Deployment**: Ready for containerization

## 📁 Project Structure

```
├── app.py                 # Flask web server
├── index.html            # Web interface
├── train_model.py        # Model training script
├── clean_dataset.py      # Data preprocessing
├── feature_extractor.py  # URL feature extraction
├── test_url.py          # Model testing utilities
├── requirements.txt      # Python dependencies
├── clean_urls.csv       # Processed training data
├── malicious_phish.csv  # Additional dataset
├── PhiUSIIL_Phishing_URL_Dataset.csv  # Original dataset
└── __pycache__/         # Python cache
```

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phishing-url-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model** (optional - pre-trained models included)
   ```bash
   python train_model.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📖 Usage

### Web Interface
1. Open `index.html` in your browser
2. Enter a URL in the input field
3. Click "Analyze" to get instant results
4. View detailed analysis including confidence scores

### API Usage
```python
import requests

url = "https://suspicious-site.com"
response = requests.post("http://localhost:5000/predict", 
                        json={"url": url})
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")
```

### Response Format
```json
{
  "prediction": "safe|suspicious|unsafe",
  "confidence": "85.3",
  "reason": "Known trusted domain",
  "details": {
    "ml_probability": 0.123,
    "rule_adjustment": 0.045
  }
}
```

## 🧠 How It Works

1. **Feature Extraction**: URLs are analyzed for structural patterns
2. **Text Vectorization**: Character n-grams converted to TF-IDF vectors
3. **ML Prediction**: Logistic regression model predicts phishing probability
4. **Heuristic Adjustment**: Rules for known safe/risky domains applied
5. **Final Scoring**: Combined ML + rule-based probability determines verdict

## 📊 Datasets

- **PhiUSIIL Phishing URL Dataset**: Large-scale dataset with 54 features
- **Clean URLs**: Processed dataset with URL text and binary labels
- **Malicious Phish**: Additional phishing samples for validation

## 🔍 Model Artifacts

The following files are generated during training:
- `url_phishing_model.pkl`: Trained logistic regression model
- `tfidf_vectorizer.pkl`: TF-IDF vectorizer for text features
- `scaler.pkl`: Standard scaler for structural features

## 🚨 Security Features

- **Safe Domain Whitelist**: Known trusted domains (Google, PayPal, etc.)
- **Risky Host Detection**: Suspicious hosting platforms
- **Domain Analysis**: Checks for excessive dots, hyphens
- **Protocol Validation**: HTTP vs HTTPS scoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## ⚠️ Disclaimer

This tool provides automated analysis but should not be the sole method for determining URL safety. Always exercise caution and use multiple verification methods for critical security decisions.