from flask import Flask, request, jsonify
from pathlib import Path
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# Configure the Google Generative AI
genai.configure(api_key="AIzaSyATPDTtRq7BAP027y-M2j2ztBjq3emqGfE")

# Set up the model configuration
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8000,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Define the API endpoint for content generation
@app.route('/generate_content', methods=['POST'])
def generate_content():
    # Check for both image and text in the request
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Both image file and text are required"}), 400

    image_file = request.files['image']
    user_text = request.form['text']  # Retrieve text from the form data
    image_path = Path(image_file.filename)
    image_path.write_bytes(image_file.read())

    if not image_path.exists():
        return jsonify({"error": "Could not process the image"}), 500

    # Prepare the prompt with the image and user-provided text data
    image_parts = [{"mime_type": "image/jpeg", "data": image_path.read_bytes()}]
    fixed_text = "Analyze the image and the provided text both data deeply. After analyzing both the image and text data, write a detailed diet plan and exercise plan according to the provided image and text data. The diet and exercise plan should include proper numbering, headings, and subheadings. Prepare a detailed plan of approximately 1000 words with extra tips and suggestions."
    
    prompt_parts = [
        user_text,  # User-provided text
        " ",
        fixed_text,
        image_parts[0],
        
    ]

    # Generate content using the model
    response = model.generate_content(prompt_parts)
    return jsonify({"response": response.text})

