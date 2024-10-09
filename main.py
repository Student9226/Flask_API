from flask import Flask, request, jsonify
from boltiotai import openai
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)
openai.api_key = os.environ['OPENAI_API_KEY']

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome Page</title>
    </head>
    <body>
        <h1 style="text-align:center">You are viewing the Flask app serving as NLP backend to my CO-PO Mapper Website!</h1>
        <p style="text-align:center">To view the website this Flask app is intended for, go to <a href="http://www.copomapper.surge.sh" target="_blank">CO PO Mapper</a>.</p>
        <p style="text-align:center">Feel free to explore!</p>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json.get('data')

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    formatted_data = format_data_for_ai(data)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "You are a course outcomes - program outcomes mapping system."
        }, {
            "role": "user",
            "content": f"Analyze this data and determine compatibility between course outcomes and program outcomes. Data: {formatted_data}"
        }]
    )

    output = response['choices'][0]['message']['content']

    return jsonify({'result': output})

def format_data_for_ai(data):
    formatted_data = ""
    for row in data:
        formatted_data += f"Course: {row['course']}, Outcome: {row['outcome']}\n"
    return formatted_data

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json  
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant for my CO-PO Mapper website. Answer and guide user's queries in very concise and short reponse; giving only as much response as needed. You can use the following data about my website to satisfy user's doubts: The sidebar that can be opned by the hamburger icon on the top-right contains navigation buttons to Home, Contact, About and Login pages. The website is currently in its newly developed stage and more updates are on the way. User's must input accurate and complete data in the table to receive accurate CO-PO mapping. The dark-mode button on the top-left changes the website's theme. Frequently asked questions can be found on the About page which also contains more information about the website and its functionality. Any suggestions can be sent on the Contact page."
        }, {
            "role": "user",
            "content": question
        }]
    )

    output = response['choices'][0]['message']['content']

    return jsonify({'answer': output})
