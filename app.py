from flask import Flask, jsonify, abort, render_template,url_for,request, send_from_directory, make_response
from flask_cors import CORS, cross_origin
from client import OpenAlexHarvester
import pandas as pd
import os


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/data/uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/process-data', methods=['GET', 'POST'])
def process_data():
    if request.method == 'POST':
        source_type = request.form.get('source_type')
        try:
            if source_type == 'api':
                # Get the URL from the POST request
                url = request.form.get('url')
                email = request.form.get('email')
                # Perform your internal data processing here
                harvester = OpenAlexHarvester(api_url=url,email=email)
                metadata_list = harvester.harvest_metadata(per_page=50)
            elif source_type == 'csv':
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                    
                file = request.files['file']
                if file.filename == '' or not allowed_file(file.filename):
                    return jsonify({'error': 'Invalid file'}), 400

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                try:
                    harvester = OpenAlexHarvester(csv_filepath=filepath)
                    metadata_list = harvester.process_csv_data()
                    # Clean up the uploaded file
                    #os.remove(filepath)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            else:
                return jsonify({'error': 'Invalid source type'}), 400

            return jsonify(metadata_list)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/')
def homePage():
    return render_template('home.html') 
                             
if __name__ == '__main__':
    app.run(debug=True,port=5000, host='0.0.0.0')  