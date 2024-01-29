from flask import Flask, request, redirect, jsonify
from flasgger import Swagger
import sqlite3
import hashlib

app = Flask(__name__)
swagger = Swagger(app)

def generate_short_url(original_url):
    hash_object = hashlib.md5(original_url.encode())
    # print(str(hash_object.hexdigest()))
    return hash_object.hexdigest()[:7]

def get_db_connection():
    connection = sqlite3.connect('urls.db')
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_db_connection()
    connection.execute('''CREATE TABLE IF NOT EXISTS urls(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       original_url TEXT NOT NULL,
                       short_url TEXT NOT NULL)''')
    connection.commit()
    connection.close()


@app.route('/shorten', methods=['POST'])
def shorten():
    """
    Shorten a URL
    ---
    parameters:
        - name: url
          in: body
          type: string
          required: true
          example: {"url": "http://www.google.com" }
    responses:
      200:
        description: A short URL
    """
    original_url = request.json['url']
    short_url = generate_short_url(original_url)

    db_connection = get_db_connection()
    # insert short_url and original_url into db
    db_connection.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
    db_connection.commit()
    db_connection.close()

    return jsonify({'short_url': short_url})

@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    """
    Get an Original URL
    ---
    parameters:
        - name: short_url
          in: path
          type: string
          required: true
    responses:
      200:
        description: Original URL
      404:
        description: URL Not Found

    """
    db_connection = get_db_connection()
    # insert short_url and original_url into db
    url_data = db_connection.execute('SELECT original_url FROM urls WHERE short_url = ?',(short_url,)).fetchone()
    print(url_data)
    db_connection.close()

    if url_data:
        # return redirect(url_data['original_url'])
        return jsonify({"original_url": url_data['original_url']}), 200
    return 'URL not found!', 404

if __name__ == '__main__':
    create_table()
    app.run(debug=True, port=8088)