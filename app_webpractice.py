from flask import Flask, render_template, redirect, request, url_for
import json

app = Flask(__name__)

app.config['FILE'] = None
app.config['FILE_DATA'] = None

@app.route('/')
def index():
    app.config['FILE'] = None
    app.config['FILE_DATA'] = None
    error=None
    result = None
    file_current = app.config['FILE'].filename if app.config['FILE'] else None
    return render_template('index.html', result=result, file_name=file_current, error=error)

@app.route('/message/<message_id>', methods=['POST', 'GET'])
def message(message_id):
    error=None
    message=None
    jsfile = app.config['FILE']
    jsfile_name = jsfile.filename
    data = app.config['FILE_DATA']
    try: 
        if message_id in data:
            message = data[message_id]  
        else: 
            raise KeyError
    except KeyError:
        error = "Sorry, we do not have data on that. Please try again."
    #import pdb;pdb.set_trace()
    return render_template('index.html', file_name=jsfile_name, result=message, message_id=message_id, error=error)

@app.route('/submit', methods=['POST'])
def submit():
    
    input_file = request.files.get('myfile_name')
    #get file extension --- this can process json files only
    
    file_ext = input_file.filename.split('.')[-1] if input_file else ''
    
    #check if file is present and it must be json
    #this can process json files only
    if input_file:
        if file_ext.lower() == 'json':
            app.config['FILE'] = input_file
            app.config['FILE_DATA'] = json.load(app.config['FILE'])
        else:
            error = "Chosen file is not a JSON file. Please try again"
            return render_template('index.html', result=None, error=error)
            
    elif not input_file and app.config['FILE']==None:
        error = "No file selected. Please choose a JSON file."
        return render_template('index.html', result=None, error=error)
    
    
    message_id = request.form['message_number']

    return redirect(url_for('message',message_id=message_id))


if __name__ == "__main__":
    app.run(debug=True)
