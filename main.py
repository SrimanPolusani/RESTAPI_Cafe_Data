# <--------IMPORT STATEMENTS-------->
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
# passcode file is not added for obvious reasons
from passcode import api_key_top_secret

app = Flask(__name__)
# <--------CREATE DB-------->
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


# <--------CREATE TABLE-------->
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# <--------GET A RANDOM CAFE-------->
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


# <--------GET ALL CAFES DATA-------->
@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


# <--------GET CAFES DATA AT SPECIFIC LOCATION-------->
@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("location")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()

    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(
            error={
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        ), 404


# <--------ADD NEW CAFE TO THE DATABASE-------->
@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(
        response={
            "success": "Successfully added the new cafe."
        }
    )


# <--------TO CHANGE THE DETAILS FOR A CAFE IN THE DATABASE-------->
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)

    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(
            response={
                "success": "Successfully updated the price"
            }
        ), 200
    else:
        return jsonify(
            error={
                "Not Found": "Sorry a cafe with that id was not found in the database"
            }
        ), 404


# <--------DELETE A CAFE FROM THE DATABASE-------->
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")

    if api_key == api_key_top_secret:
        cafe = db.session.query(Cafe).get(cafe_id)

        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(
                response={
                    "success": "Successfully deleted the cafe from the database"
                }
            ), 200
        else:
            return jsonify(
                error={
                    "Not Found": "Sorry a cafe with that id was not found in the database"
                }
            ), 404

    else:
        return jsonify(
            error={
                "Forbidden": "You are not authorized to access this route"
            }
        ), 403


if __name__ == '__main__':
    app.run(debug=True)
