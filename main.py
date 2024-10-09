from flask import Flask, request, jsonify
from boltiotai import openai
from dotenv import load_dotenv
import os
from flask_cors import CORS
from pymongo import MongoClient

load_dotenv()
app = Flask(__name__)
CORS(app)
openai.api_key = os.environ['OPENAI_API_KEY']
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client['co_po_mapping']
course_collection = db['courses'] 
program_collection = db['programs'] 

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
@app.route('/add_course', methods=['POST'])
def add_course():
    """
    Adds course outcomes to MongoDB.
    Expected data format: { "course": "Course Name", "outcomes": [ "CO1", "CO2", "CO3" ] }
    """
    data = request.json
    course_name = data.get('course')
    outcomes = data.get('outcomes')

    if not course_name or not outcomes:
        return jsonify({'error': 'Course name or outcomes missing'}), 400

    course_collection.insert_one({'course': course_name, 'outcomes': outcomes})
    return jsonify({'message': 'Course outcomes added successfully'}), 201

@app.route('/add_program', methods=['POST'])
def add_program():
    """
    Adds program outcomes to MongoDB.
    Expected data format: { "program": "Program Name", "outcomes": [ "PO1", "PO2", "PO3" ] }
    """
    data = request.json
    program_name = data.get('program')
    outcomes = data.get('outcomes')

    if not program_name or not outcomes:
        return jsonify({'error': 'Program name or outcomes missing'}), 400

    program_collection.insert_one({'program': program_name, 'outcomes': outcomes})
    return jsonify({'message': 'Program outcomes added successfully'}), 201

@app.route('/get_course/<course_name>', methods=['GET'])
def get_course(course_name):
    """
    Retrieves course outcomes from MongoDB.
    """
    course = course_collection.find_one({'course': course_name}, {'_id': 0})

    if course:
        return jsonify(course), 200
    return jsonify({'error': 'Course not found'}), 404

@app.route('/get_program/<program_name>', methods=['GET'])
def get_program(program_name):
    """
    Retrieves program outcomes from MongoDB.
    """
    program = program_collection.find_one({'program': program_name}, {'_id': 0})

    if program:
        return jsonify(program), 200
    return jsonify({'error': 'Program not found'}), 404
@app.route('/get_mapping/<program_name>/<course_name>', methods=['GET'])
def get_mapping(program_name, course_name):
    mapping = db.mappings.find_one(
        {program_name: {"$exists": True}},
        {program_name: {course_name: 1, "_id": 0}}
    )

    if mapping:
        return jsonify(mapping), 200
    return jsonify({'error': 'Mapping not found'}), 404

@app.route('/get_all_courses', methods=['GET'])
def get_all_courses():
    courses = list(course_collection.find({}, {'_id': 0}))
    return jsonify(courses), 200

@app.route('/get_all_programs', methods=['GET'])
def get_all_programs():
    programs = list(program_collection.find({}, {'_id': 0}))
    return jsonify(programs), 200

if __name__ == '__main__':
    app.run(debug=True)