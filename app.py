from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload or form submission
        uploaded_file = request.files.get('file_upload')
        if uploaded_file:
            # Perform processing here
            result = "Tampering Not Detected"  # Example result
            return render_template('index.html', pred=result)
        return render_template('index.html', pred="No file uploaded.")
    
    # For GET requests
    return render_template('index.html', pred="")
