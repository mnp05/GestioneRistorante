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
        user = auth_ctrl.handle_login(data.get("email"), data.get("password"))
        return jsonify({"status": "success", "user": user}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = auth_ctrl.handle_signup(
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
        user = auth_ctrl.handle_create_employee(
            data.get("creatore_id"), data.get("nome"), data.get("cognome"),
            data.get("email"), data.get("password"), data.get("livello_accesso")
        )
        return jsonify({"status": "success", "user": user}), 201
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403

@app.route('/api/auth/dipendenti', methods=['GET'])
def get_dipendenti():
    return jsonify({"status": "success", "data": auth_ctrl.handle_get_all_employees()}), 200

@app.route('/api/auth/dipendente/<dipendente_id>', methods=['PUT'])
def update_dipendente(dipendente_id):
    data = request.json
    try:
        success = auth_ctrl.handle_modify_access_level(data.get("creatore_id"), dipendente_id, data.get("livello_accesso"))
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Dipendente non trovato"}), 404
    except (PermissionError, ValueError) as e:
        return jsonify({"status": "error", "message": str(e)}), 403

@app.route('/api/auth/dipendente/<dipendente_id>', methods=['DELETE'])
def delete_dipendente(dipendente_id):
    data = request.json or {}
    try:
        success = auth_ctrl.handle_remove_employee(data.get("creatore_id"), dipendente_id) # type: ignore
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Dipendente non trovato"}), 404
    except (PermissionError, ValueError) as e:
        return jsonify({"status": "error", "message": str(e)}), 403

# --- PRENOTAZIONI E TAVOLI ---

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    cliente_id = request.args.get('clienteId')
    data_filtro = request.args.get('data')
    bookings = booking_ctrl.handle_get_all_bookings(data_filtro) # type: ignore 
    if cliente_id:
        bookings = [b for b in bookings if str(b.get("cliente_id")) == cliente_id]
    return jsonify({"status": "success", "data": bookings}), 200

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    result = booking_ctrl.handle_new_booking(data)
    return jsonify({"status": "success", "data": result}), 201

@app.route('/api/bookings/<booking_id>', methods=['PUT'])
def update_booking(booking_id):
    data = request.json
    if data.get("stato") == "CONFERMATA" and data.get("tavolo_id"):
        success = booking_ctrl.handle_confirm_booking(booking_id, data.get("tavolo_id"))
    else:
        success = booking_ctrl.handle_edit_booking(booking_id, data) # type: ignore
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Prenotazione non trovata"}), 404

@app.route('/api/bookings/<booking_id>/auto_confirm', methods=['POST'])
def auto_confirm_booking(booking_id):
    tavolo_id = booking_ctrl.handle_try_auto_confirm(booking_id)
    if tavolo_id:
        return jsonify({"status": "success", "tavolo_id": tavolo_id}), 200
    return jsonify({"status": "error", "error_code": "OVERBOOKING", "message": "Nessun tavolo compatibile libero."}), 400

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    success = booking_ctrl.handle_cancel_booking(booking_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Prenotazione non trovata"}), 404

@app.route('/api/tables', methods=['GET'])
def get_tables():
    data_filtro = request.args.get('data')
    return jsonify({"status": "success", "data": booking_ctrl.handle_get_tables(data_filtro)}), 200 # type: ignore

@app.route('/api/tables/<numero>', methods=['PUT'])
def update_table_status(numero):
    data = request.json
    target_date = data.get("data", "DEFAULT")
    success = booking_ctrl.handle_table_status_update(numero, data.get("stato"), target_date)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Tavolo non trovato"}), 404


@app.route('/api/tables', methods=['POST'])
def add_or_update_table():
    data = request.json
    try:
        tavolo = booking_ctrl.handle_table_layout_update(data)
        return jsonify({"status": "success", "data": tavolo}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/tables/<numero>', methods=['DELETE'])
def delete_table(numero):
    target_date = request.args.get('data', 'DEFAULT')
    try:
        success = booking_ctrl.handle_remove_table(numero, target_date)
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Tavolo non trovato"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# --- MENU ---

@app.route('/api/menu', methods=['GET'])
def get_menu():
    is_staff = request.args.get('all', 'false').lower() == 'true'
    if is_staff:
        return jsonify({"status": "success", "data": menu_ctrl.get_all_menu()}), 200
    return jsonify({"status": "success", "data": menu_ctrl.get_filtered_menu()}), 200

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    item = menu_ctrl.add_product(data)
    return jsonify({"status": "success", "data": item}), 201

@app.route('/api/menu/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    success = menu_ctrl.edit_product(item_id, data)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Piatto non trovato"}), 404

@app.route('/api/menu/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    success = menu_ctrl.deactivate_product(item_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Piatto non trovato"}), 404

@app.route('/api/menu/<item_id>/activate', methods=['PUT'])
def activate_menu_item(item_id):
    success = menu_ctrl.activate_product(item_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Piatto non trovato"}), 404

# --- PREFERITI MENU ---

@app.route('/api/menu/preferiti/<cliente_id>', methods=['GET'])
def get_preferiti(cliente_id):
    try:
        preferiti = menu_ctrl.get_favorites(cliente_id)
        return jsonify({"status": "success", "data": preferiti}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/menu/preferiti/<cliente_id>', methods=['POST'])
def toggle_preferito(cliente_id):
    data = request.json
    piatto_id = data.get("piatto_id")
    try:
        is_added = menu_ctrl.toggle_favorite(cliente_id, piatto_id)
        return jsonify({"status": "success", "is_added": is_added}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# --- INVENTARIO ---

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify({"status": "success", "data": inv_ctrl.get_inventory()}), 200

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    data = request.json
    item = inv_ctrl.add_stock_item(data)
    return jsonify({"status": "success", "data": item}), 201

@app.route('/api/inventory/<item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    success = inv_ctrl.update_stock_quantity(item_id, float(data.get("quantita_disponibile")))
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Ingrediente non trovato"}), 404

@app.route('/api/inventory/<item_id>/full', methods=['PUT'])
def update_inventory_full(item_id):
    data = request.json
    success = inv_ctrl.edit_stock_item(item_id, data)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Ingrediente non trovato"}), 404

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    success = inv_ctrl.remove_stock_item(item_id)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Ingrediente non trovato"}), 404


@app.route('/api/inventory/categories', methods=['GET'])
def get_inventory_categories():
    return jsonify({"status": "success", "data": inv_ctrl.get_categories()}), 200

@app.route('/api/inventory/categories/<nome>', methods=['DELETE'])
def delete_inventory_category(nome):
    success = inv_ctrl.remove_category(nome)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Impossibile rimuovere la categoria"}), 400


# --- PROMOZIONI ---

@app.route('/api/promo/punti/<cliente_id>', methods=['GET'])
def get_punti(cliente_id):
    storico = promo_ctrl.get_accumulated_points(cliente_id)
    return jsonify({"status": "success", "data": storico}), 200

@app.route('/api/promo/buoni/<cliente_id>', methods=['GET'])
def get_buoni(cliente_id):
    buoni = promo_ctrl.get_user_gift_cards(cliente_id)
    return jsonify({"status": "success", "data": buoni}), 200

@app.route('/api/promo/buoni', methods=['POST'])
def acquista_buono():
    data = request.json
    buono = promo_ctrl.buy_gift_card(
        data.get("acquirente_id"), float(data.get("valore")), data.get("data_scadenza")
    )
    return jsonify({"status": "success", "data": buono}), 201

@app.route('/api/promo/riscatta', methods=['POST'])
def riscatta_buono():
    data = request.json
    try:
        buono = promo_ctrl.redeem_gift_card(data.get("codice"), data.get("beneficiario_id"))
        return jsonify({"status": "success", "data": buono}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# --- DASHBOARD ---

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_messages():
    return jsonify({"status": "success", "data": dash_ctrl.get_all_messages()}), 200

@app.route('/api/dashboard', methods=['POST'])
def post_dashboard_message():
    data = request.json
    try:
        msg = dash_ctrl.add_message(data.get("testo"), data.get("autore_id"))
        return jsonify({"status": "success", "data": msg}), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/dashboard/<msg_id>', methods=['PUT'])
def update_dashboard_message(msg_id):
    data = request.json
    try:
        success = dash_ctrl.edit_message(msg_id, data.get("autore_id"), data.get("testo"))
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Messaggio non trovato"}), 404
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403

@app.route('/api/dashboard/<msg_id>', methods=['DELETE'])
def delete_dashboard_message(msg_id):
    data = request.json or {}
    try:
        success = dash_ctrl.remove_message(msg_id, data.get("utente_id"), data.get("ruolo")) # type: ignore
        if success:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Messaggio non trovato"}), 404
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
