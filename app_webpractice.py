from flask import Flask, render_template, request, session, redirect, url_for
import importlib.metadata, sys
import json
import mimetypes
import os
import uuid

app = Flask(__name__)
app.secret_key = 'secret606560'  # Use a secure, random secret key in production
flask_version = importlib.metadata.version("flask")


# Configuration for temporary file storage
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('homepage.html', flask_ver=flask_version, python_ver=sys.version.split(' ')[0])

@app.route('/message-index')
def index():
    # Clear session data on home, including the stored file path
    if 'uploaded_file_path' in session:
        try:
            os.remove(session['uploaded_file_path'])
        except OSError:
            pass # Ignore if file doesn't exist or permission error
    session.clear()
    return render_template('index.html', result=None, file_name=None, error=None, current_message_id=None)

#CALCULATOR PAGE 
@app.route('/calc-add')
def calculate_sum():
    return render_template('calculator.html', sum=None, num1=None, num2=None)

@app.route('/sum', methods=['POST'])
def add_nums():
    num1 = request.form.get('num1')
    num2 = request.form.get('num2')
    #import pdb;pdb.set_trace()
    sum = int(num1) + int(num2)
    
    return render_template('calculator.html', num1=num1, num2=num2, sum=sum)

# Route to handle file uploads and initial message_id submission
@app.route('/upload_and_query', methods=['POST'])
def upload_and_query():
    error = None
    uploaded_file_name = session.get('uploaded_file_name')
    uploaded_file_path = session.get('uploaded_file_path')

    # Handle file upload
    input_file = request.files.get('myfile_name')
    if input_file and input_file.filename != '':
        mimetype = mimetypes.guess_type(input_file.filename)[0]
        if mimetype == 'application/json':
            try:
                # Clean up previous file if a new one is uploaded
                if uploaded_file_path and os.path.exists(uploaded_file_path):
                    os.remove(uploaded_file_path)

                unique_filename = str(uuid.uuid4()) + os.path.splitext(input_file.filename)[1]
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                input_file.save(save_path)

                session['uploaded_file_name'] = input_file.filename
                session['uploaded_file_path'] = save_path
                uploaded_file_name = input_file.filename

                # Test if the file is valid JSON immediately after saving
                with open(save_path, 'r') as f:
                    json.load(f) # Just load to test validity

            except json.JSONDecodeError:
                error = "Invalid JSON format. Please upload a valid JSON file."
                if os.path.exists(save_path): os.remove(save_path)
                session.pop('uploaded_file_name', None)
                session.pop('uploaded_file_path', None)
                return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)
            except Exception as e:
                error = f"An unexpected error occurred during file upload: {e}"
                if os.path.exists(save_path): os.remove(save_path)
                session.pop('uploaded_file_name', None)
                session.pop('uploaded_file_path', None)
                return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)
        else:
            error = "Chosen file is not a JSON file. Please try again."
            return render_template('index.html', result=None, error=error, file_name=uploaded_file_name, current_message_id=None)
    elif not uploaded_file_path: # No new file uploaded and no path in session
        error = "No file selected or no JSON data found from a previous upload. Please choose a JSON file."
        return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)

    # Get the message ID from the form after file handling
    message_id_from_form = request.form.get('message_number', '').strip()
    if not message_id_from_form:
        error = "Please enter a message number."
        # If there was a successful file upload but no message ID, render with error
        return render_template('index.html', result=None, error=error, file_name=session.get('uploaded_file_name'), current_message_id=None)

    # Redirect to the /message/<message_id> route
    return redirect(url_for('show_message', message_id=message_id_from_form))


# Route to display a specific message based on message_id in URL
@app.route('/message/<message_id>', methods=['GET'])
def show_message(message_id):
    error = None
    message_result = None
    uploaded_file_name = session.get('uploaded_file_name')
    uploaded_file_path = session.get('uploaded_file_path')

    if not uploaded_file_path:
        error = "No JSON file has been uploaded yet. Please go to the home page and upload one."
        return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)

    json_data = None
    try:
        with open(uploaded_file_path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        error = "Uploaded file not found on the server. Please re-upload the file."
        session.pop('uploaded_file_name', None)
        session.pop('uploaded_file_path', None)
        return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)
    except json.JSONDecodeError:
        error = "The stored file is corrupted or not valid JSON. Please re-upload the file."
        session.pop('uploaded_file_name', None)
        session.pop('uploaded_file_path', None)
        return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)
    except Exception as e:
        error = f"Error loading stored file: {e}. Please re-upload the file."
        session.pop('uploaded_file_name', None)
        session.pop('uploaded_file_path', None)
        return render_template('index.html', result=None, error=error, file_name=None, current_message_id=None)

    if json_data:
        if message_id in json_data:
            message_result = json_data[message_id]
        else:
            error = f"Sorry, message ID '{message_id}' not found in the uploaded data. Please try again."
    else:
        error = "No JSON data available to query. This should not happen if `uploaded_file_path` exists."

    return render_template('index.html', file_name=uploaded_file_name, result=message_result, current_message_id=message_id, error=error)

#To So list page
@app.route('/to-do', methods=['GET'])
def add_task():
    return render_template('to_do.html')

if __name__ == "__main__":
    app.run(debug=True)