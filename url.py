from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'url.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(80), unique=True)
    long = db.Column(db.String(120), unique=True)

    def __init__(self, short, long):
        self.short = short 
        self.long = long 


class URLSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('short', 'long')


url_schema = URLSchema()
urls_schema = URLSchema(many=True)

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num, alphabet=BASE62):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def decode(string, alphabet=BASE62):
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

current_random_id = 12445688

def generate_short_url():
    global current_random_id
    while True:
        short = encode(current_random_id)
        current_random_id += 1
        #existing = db.get({'short': short})
    	existing = URL.query.get(short)
        if not existing:
            return short 

# endpoint to create shorter URL 
@app.route("/short", methods=["POST"])
def shortener():
    long = request.json['destination']
    short = generate_short_url();
    
    new_url = URL(short, long)

    db.session.add(new_url)
    db.session.commit()

    response_body = { 'url': short};

    return jsonify(response_body)


@app.route("/short", methods=["GET"])
def get_url():
    all_urls = URL.query.all()
    result = urls_schema.dump(all_urls)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/short/<id>", methods=["GET"])
def url_detail(id):
    url = URL.query.filter_by(short=id).first()
    return url_schema.jsonify(url)


# endpoint to get user detail by id
@app.route("/short/deleteAll", methods=["GET"])
def url_deleteAll():
    URL.query.delete()

    return jsonify("done")

if __name__ == '__main__':
    app.run(debug=True)


