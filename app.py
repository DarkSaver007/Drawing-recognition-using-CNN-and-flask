import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from keras.models import Model
from model_utils import make_keras_picklable  # Import the function from model_utils
from PIL import Image
import base64
import io
import os

# Run the hotfix function to enable pickling
make_keras_picklable()

# Initialize Flask app
app = Flask(__name__)

# Helper function to read HTML file (for serving draw.html and results.html)
def read_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Function to preprocess the image data for prediction
def preprocess_image(img_data):
    """Process the base64 image into the correct shape for the model."""
    img = Image.open(io.BytesIO(base64.b64decode(img_data.split(',')[1])))
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((28, 28))  # Resize to 28x28
    img = np.array(img, dtype='float32') / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

# Load the trained model (use pickle)
def load_pickled_model(filename):
    try:
        with open(filename, 'rb') as f:
            model = pickle.load(f)
            print("Pickled model loaded successfully!")
            return model
    except Exception as e:
        print(f"Error loading pickled model: {e}")
        return None

# Load the trained model
model = load_pickled_model('model_cnn.pkl')

# Route for serving the home page (draw.html)
@app.route('/')
def home():
    draw_html = read_from_file('draw.html')  # Directly load from the file system
    return render_template_string(draw_html)

# Route for handling the prediction
class_names = ['eye', 'arm', 'face', 'finger', 'hand', 'leg', 'mouth', 'nose', 'ear']

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    img_data = data['image']
    
    # Preprocess the image data
    img = preprocess_image(img_data)
    
    # Get model predictions if the model is loaded
    if model:
        prediction = model.predict(img)
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        
        # Get the class name corresponding to the predicted index
        predicted_class_name = class_names[predicted_class_index]
        
        # Return the prediction as a JSON response with the class name
        return jsonify({'prediction': predicted_class_name})
    else:
        return jsonify({'error': 'Model is not loaded'}), 500

# Route for the results page
@app.route('/results')
def results():
    prediction = request.args.get('prediction')
    
    # Read the results.html file manually from the root directory
    file_path = 'results.html'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            results_html = file.read()
    else:
        # If the file doesn't exist, return a simple error message
        results_html = "<h1>Results Page Not Found</h1>"
    
    # Replace the placeholder with the actual prediction in the HTML content
    results_html = results_html.replace('{{ prediction }}', prediction if prediction else "Nothing to predict!")
    
    # Return the final HTML content with prediction
    return render_template_string(results_html)

# Run the Flask app
if __name__ == '__main__':
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
