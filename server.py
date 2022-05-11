from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import json
import os

load_dotenv()
print(os.getenv('MONGODB_URI'))
client = MongoClient(os.getenv('MONGODB_URI'))

db = client['shopify-inventory']

inv = db.inventories
wh = db.warehouses


def update_warehouse_stock(old, new, quantity):
    old_wh = wh.find_one({'name': old})
    new_wh = wh.find_one({'name': new})

    if not new_wh:
        return False

    if old_wh:
        if old_wh['stock'] > 0:
            old_wh['stock'] = int(old_wh['stock']) - int(quantity)
        wh.update_one({'name': old}, {'$set': old_wh})

    new_wh['stock'] = int(new_wh['stock']) + int(quantity)

    wh.update_one({'name': new}, {'$set': new_wh})

    return True


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
            return redirect('/')
        else:
            return redirect('/add')


# delete inventory


@app.route('/delete', methods=['GET', 'POST'])
def remove_imventory():
    inventories = list(inv.find())
    if request.method == 'GET':
        return render_template('remove.html', inv=inventories)
    else:
        model = request.form['model_number']
        product = inv.find_one({'model': model})
        if product.get('warehouse'):
            p_wh = wh.find_one({'name': product['warehouse']})
            p_wh['stock'] -= product['quantity']
            wh.update_one({'model': product['model']}, {'$set': p_wh})

        inv.delete_one({'model': product['model']})
        return redirect('/')


@app.route('/modify', methods=['GET', 'POST'])
def update_inventory():
    houses = list(wh.find())
    inventories = list(inv.find())
    if request.method == 'GET':

        return render_template('modify.html', wh=houses, inv=inventories)

    else:
        model = request.form['model_number']
        name = request.form['name']
        quantity = request.form['quantity']
        warehouse = request.form['warehouse']
        old_warehouse = ""

        record = inv.find_one({"model": model})
        if record.get('warehouse'):
            old_warehouse = record['warehouse']

        if record:
            if name:
                record['name'] = name
            if quantity:
                record['quantity'] = quantity
            if warehouse:
                record['warehouse'] = warehouse
                update_warehouse_stock(
                    old_warehouse, warehouse, record['quantity'])

            inv.update_one({'model': model}, {'$set': record})
            return redirect('/')
        else:
            return redirect('/modify', wh=houses, inv=inventories)

# view inventory


@app.route('/view')
def display_inventory():
    curr = list(inv.find())
    return render_template("view.html", inv=curr)

# add warehouse/locations


@app.route('/add_warehouse', methods=['GET', 'POST'])
def add_warehouse():
    if request.method == 'GET':
        return render_template('add_warehouse.html')
    else:
        house_name = request.form['house_name']
        house_address = request.form['house_address']

        obj = {'name': house_name, 'address': house_address, 'stock': 0}

        try:
            wh.insert_one(obj)
            return redirect('/')

        except:
            return redirect('/add_warehouse')

# view warehouses and current stock


@app.route('/view_warehouse')
def view_warehouse():
    houses = list(wh.find())
    return render_template('view_warehouse.html', wh=houses)


if __name__ == '__main__':
    app.run(debug=True)
