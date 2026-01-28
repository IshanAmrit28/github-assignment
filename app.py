from flask import Flask, jsonify, render_template, request, redirect, url_for
import json
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.flask_db
collection = db.submissions
todo_collection = db.todo_items


# task 1 api endpoint
@app.route("/api", methods=["GET"])
def get_data():
    try:
        file_path = os.path.join(app.root_path, "data.json")
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# task 2 mongo and form handling
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        try:
            if not name or not email:
                raise ValueError("All fields are required")

            collection.insert_one({"name": name, "email": email})

            return redirect(url_for("success"))

        except (PyMongoError, ValueError) as e:
            error = f"Error during submission: {str(e)}"

    return render_template("index.html", error=error)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/todo")
def todo():
    return render_template("todo.html")


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    try:
        item_name = request.form.get("itemName")
        item_description = request.form.get("itemDescription")

        if not item_name or not item_description:
            return jsonify({"error": "All fields are required"}), 400

        todo_collection.insert_one(
            {"itemName": item_name, "itemDescription": item_description}
        )

        return jsonify({"message": "To-Do item added successfully"}), 201

    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
