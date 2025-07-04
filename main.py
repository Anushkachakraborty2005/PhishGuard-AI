from flask import Flask, render_template, request
import google.generativeai as genai
import os
import PyPDF2

app = Flask(__name__)

genai.configure(api_key="AIzaSyCxxCBerA6Zv9hvU-wJEfpis8ARsw_wFvY")
model = genai.GenerativeModel("gemini-1.5-flash")

def predict_fake_or_real_email_content(text):
    prompt = f"""
    You are an expert in identifying scam messages in text, email etc. Analyze the given text and classify it as:

    - *Real/Legitimate* (Authentic, safe message)
    - *Scam/Fake* (Phishing, fraud, or suspicious message)

    *for the following Text:*
    {text}

    **Return a clear message indicating whether this content is real or a scam.
    If it is a scam, mention why it seems fraudulent. If it is real, state that it is legitimate.**

    *Only return the classification message and nothing else.*
    Note: Don't return empty or null, you only need to return message for the input text
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Classification failed: No response from model."
    except Exception as e:
        return f"Classification error: {e}"

def url_detection(url):
    prompt = f"""
    You are an advanced AI model specializing in URL security classification. Analyze the given URL and classify it as one of the following categories:

    1. Benign**: Safe, trusted, and non-malicious websites such as google.com, wikipedia.org, amazon.com.
    2. Phishing**: Fraudulent websites designed to steal personal information. Indicators include misspelled domains (e.g., paypa1.com instead of paypal.com), unusual subdomains, and misleading content.
    3. Malware**: URLs that distribute viruses, ransomware, or malicious software. Often includes automatic downloads or redirects to infected pages.
    4. Defacement**: Hacked or defaced websites that display unauthorized content, usually altered by attackers.

    *Example URLs and Classifications:*
    - *Benign*: "https://www.microsoft.com/"
    - *Phishing*: "http://secure-login.paypa1.com/"
    - *Malware*: "http://free-download-software.xyz/"
    - *Defacement*: "http://hacked-website.com/"

    *Input URL:* {url}

    *Output Format:*
    - Return only a string class name (e.g., benign, phishing, malware, defacement).
    - Example output for a phishing site: 'phishing'

    Analyze the URL and return the correct classification (Only name in lowercase such as benign etc.
    Note: Don't return empty or null, at any cost return the corrected class
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower() if response.text else "unknown"
    except Exception as e:
        return f"Detection error: {e}"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/scam/', methods=['POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    if file.filename == '':
        return render_template("index.html", message="No selected file.")

    if file.filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        except Exception as e:
            return render_template("index.html", message=f"Error reading PDF: {e}")
    elif file.filename.endswith('.txt'):
        try:
            extracted_text = file.read().decode("utf-8")
        except Exception as e:
            return render_template("index.html", message=f"Error reading TXT: {e}")
    else:
        return render_template("index.html", message="Invalid file type. Please upload a PDF or TXT file.")

    if not extracted_text.strip():
        return render_template("index.html", message="File is empty or text could not be extracted.")

    message = predict_fake_or_real_email_content(extracted_text)
    return render_template("index.html", message=message)

@app.route('/predict', methods=['POST'])
def predict_url():
    url = request.form.get('url', '').strip()

    if not url:
        return render_template("index.html", message="Please enter a URL.", input_url="")

    if not url.startswith(("http://", "https://")):
        return render_template("index.html", message="Invalid URL format. URL must start with http:// or https://", input_url=url)

    classification = url_detection(url)
    return render_template("index.html", input_url=url, predicted_class=classification)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
