from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    css = url_for('static', filename="style.css")
    return render_template('index.html', css_path=css)

if __name__ == '__main__':
    app.run(debug=True)
