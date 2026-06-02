import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from server.controllers.auth_controller import AuthController
from server.controllers.booking_controller import BookingController
from server.controllers.menu_controller import MenuController
from server.controllers.inventory_controller import InventoryController
from server.controllers.promo_controller import PromoController
from server.controllers.dashboard_controller import DashboardController

app = Flask(__name__)

auth_ctrl = AuthController()
booking_ctrl = BookingController()
menu_ctrl = MenuController()
inv_ctrl = InventoryController()
promo_ctrl = PromoController()
dash_ctrl = DashboardController()


# --- AUTH ---

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = auth_ctrl.login(data.get("email"), data.get("password"))
        return jsonify({"status": "success", "user": user}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = auth_ctrl.register_cliente(
            data.get("nome"), data.get("cognome"),
            data.get("email"), data.get("password")
        )
        return jsonify({"status": "success", "user": user}), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/auth/dipendente', methods=['POST'])
def create_dipendente():
    data = request.json
    try:
        user = auth_ctrl.crea_dipendente(
            data.get("creatore_id"), data.get("nome"), data.get("cognome"),
            data.get("email"), data.get("password"), data.get("livello_accesso")
        )
        return jsonify({"status": "success", "user": user}), 201
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403


# --- PRENOTAZIONI E TAVOLI ---

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    return jsonify({"status": "success", "data": booking_ctrl.get_all_bookings()}), 200

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    result = booking_ctrl.effettua_prenotazione(data)
    return jsonify({"status": "success", "data": result}), 201

@app.route('/api/bookings/<booking_id>', methods=['PUT'])
def update_booking(booking_id):
    data = request.json
    if data.get("stato") == "CONFERMATA" and data.get("id_tavolo"):
        success = booking_ctrl.conferma_prenotazione(booking_id, data.get("id_tavolo"))
    else:
        success = booking_ctrl.modifica_prenotazione(booking_id, data)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Prenotazione non trovata"}), 404

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    success = booking_ctrl.annulla_prenotazione(booking_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Prenotazione non trovata"}), 404

@app.route('/api/tables', methods=['GET'])
def get_tables():
    return jsonify({"status": "success", "data": booking_ctrl.get_tavoli()}), 200

@app.route('/api/tables/<numero>', methods=['PUT'])
def update_table_status(numero):
    data = request.json
    success = booking_ctrl.aggiorna_stato_tavolo(numero, data.get("stato"))
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Tavolo non trovato"}), 404


# --- MENU ---

@app.route('/api/menu', methods=['GET'])
def get_menu():
    is_staff = request.args.get('all', 'false').lower() == 'true'
    if is_staff:
        return jsonify({"status": "success", "data": menu_ctrl.get_tutto_il_menu()}), 200
    return jsonify({"status": "success", "data": menu_ctrl.get_menu_attivo()}), 200

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    item = menu_ctrl.aggiungi_piatto(data)
    return jsonify({"status": "success", "data": item}), 201

@app.route('/api/menu/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    success = menu_ctrl.modifica_piatto(item_id, data)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Piatto non trovato"}), 404

@app.route('/api/menu/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    success = menu_ctrl.disattiva_piatto(item_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Piatto non trovato"}), 404


# --- INVENTARIO ---

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify({"status": "success", "data": inv_ctrl.get_inventario()}), 200

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    data = request.json
    item = inv_ctrl.aggiungi_ingrediente(data)
    return jsonify({"status": "success", "data": item}), 201

@app.route('/api/inventory/<item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    success = inv_ctrl.aggiorna_scorte(item_id, float(data.get("quantita_disponibile")))
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Ingrediente non trovato"}), 404

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    success = inv_ctrl.rimuovi_ingrediente(item_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Ingrediente non trovato"}), 404


# --- PROMOZIONI ---

@app.route('/api/promo/punti/<cliente_id>', methods=['GET'])
def get_punti(cliente_id):
    storico = promo_ctrl.get_storico_punti(cliente_id)
    return jsonify({"status": "success", "data": storico}), 200

@app.route('/api/promo/buoni/<cliente_id>', methods=['GET'])
def get_buoni(cliente_id):
    buoni = promo_ctrl.get_buoni_cliente(cliente_id)
    return jsonify({"status": "success", "data": buoni}), 200

@app.route('/api/promo/buoni', methods=['POST'])
def acquista_buono():
    data = request.json
    buono = promo_ctrl.acquista_buono_regalo(
        data.get("id_acquirente"), float(data.get("valore")), data.get("data_scadenza")
    )
    return jsonify({"status": "success", "data": buono}), 201

@app.route('/api/promo/riscatta', methods=['POST'])
def riscatta_buono():
    data = request.json
    try:
        buono = promo_ctrl.riscatta_buono(data.get("codice"), data.get("id_beneficiario"))
        return jsonify({"status": "success", "data": buono}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# --- DASHBOARD ---

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_messages():
    return jsonify({"status": "success", "data": dash_ctrl.get_messaggi()}), 200

@app.route('/api/dashboard', methods=['POST'])
def post_dashboard_message():
    data = request.json
    try:
        msg = dash_ctrl.pubblica_messaggio(data.get("autore_id"), data.get("testo"))
        return jsonify({"status": "success", "data": msg}), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/dashboard/<msg_id>', methods=['PUT'])
def update_dashboard_message(msg_id):
    data = request.json
    try:
        success = dash_ctrl.modifica_messaggio(msg_id, data.get("autore_id"), data.get("testo"))
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Messaggio non trovato"}), 404
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403

@app.route('/api/dashboard/<msg_id>', methods=['DELETE'])
def delete_dashboard_message(msg_id):
    data = request.json or {}
    try:
        success = dash_ctrl.rimuovi_messaggio(msg_id, data.get("utente_id"), data.get("ruolo"))
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Messaggio non trovato"}), 404
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403


if __name__ == '__main__':
    app.run(debug=True, port=5000)
