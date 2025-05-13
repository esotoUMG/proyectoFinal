from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Forzar recarga de plantillas

@app.route('/')
def home():
    js1_ = url_for('static', filename='js/scripts.js')
    css_ = url_for('static', filename='css/app.css')
    return render_template('index.html', css_path=css_, js_path1=js1_)

if __name__ == "__main__":
    app.run(debug=True)
