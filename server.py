from flask import Flask, render_template, request, redirect
import json
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(
    'mongodb+srv://jay:ktqWmru9vNA3NyGK@cluster0.r4aap.mongodb.net/shopify-inventory?retryWrites=true&w=majority')

db = client['shopify-inventory']

inv = db.inventories


app = Flask(__name__)


# home
@app.route('/')
def index():
    return render_template('index.html')

# add inventory


@app.route('/add', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'GET':
        return render_template('add.html')
    else:

        obj = {"name": request.form['name'], "model": request.form['model_number'],
               "quantity": request.form['quantity'], "date": datetime.now()}
        print(obj)
        id = inv.insert_one(obj)

        if id:
            return redirect('/view')
        else:
            return redirect('/add')
        return redirect('/view')

# delete inventory


@app.route('/delete')
def remove_imventory():
    if request.method == 'GET':
        return render_template('remove.html')
    else:
        pass


@app.route('/modify')
def update_inventory():
    if request.method == 'GET':
        return render_template('modify.html')
    else:
        pass

# view inventory


@app.route('/view')
def display_inventory():
    curr = list(inv.find())

    return render_template("view.html", inv=curr)


if __name__ == '__main__':
    app.run(debug=True)
