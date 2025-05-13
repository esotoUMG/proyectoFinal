from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    css_ = url_for('static', filename='css/app.css') #Busca el CSS generado por Gulp
    return render_template('index.html', css_path=css_)

if __name__ == '__main__':
    app.run(debug=True)
