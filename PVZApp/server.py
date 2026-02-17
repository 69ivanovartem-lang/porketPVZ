import http.server
import socketserver
import json
import sqlite3
import datetime
import urllib.parse
from http import HTTPStatus
import re

# Конфигурация сервера
PORT = 8000
HOST = 'localhost'

class PVZHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Отдаем статические файлы
        if parsed_path.path.startswith('/static/'):
            return super().do_GET()
        
        # API endpoints
        if parsed_path.path == '/api/orders':
            self.handle_get_orders(parsed_path.query)
        elif parsed_path.path == '/api/stats':
            self.handle_get_stats()
        elif parsed_path.path.startswith('/api/orders/'):
            order_id = parsed_path.path.replace('/api/orders/', '')
            self.handle_get_order(order_id)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/orders':
            self.handle_create_order()
        elif parsed_path.path == '/api/orders/issue':
            self.handle_issue_order()
        elif parsed_path.path == '/api/orders/cancel':
            self.handle_cancel_order()
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_PUT(self):
        """Обработка PUT запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path.startswith('/api/orders/'):
            order_id = parsed_path.path.replace('/api/orders/', '').replace('/status', '')
            self.handle_update_order_status(order_id)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_DELETE(self):
        """Обработка DELETE запросов"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path.startswith('/api/orders/'):
            order_id = parsed_path.path.replace('/api/orders/', '')
            self.handle_delete_order(order_id)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def handle_get_orders(self, query_string):
        """Получение списка заказов с фильтрацией"""
        params = urllib.parse.parse_qs(query_string)
        
        # Параметры фильтрации
        status = params.get('status', [None])[0]
        search = params.get('search', [None])[0]
        date_from = params.get('date_from', [None])[0]
        date_to = params.get('date_to', [None])[0]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM orders WHERE 1=1"
        args = []
        
        if status:
            query += " AND status = ?"
            args.append(status)
        
        if search:
            query += " AND (order_number LIKE ? OR client_name LIKE ? OR phone LIKE ?)"
            search_term = f"%{search}%"
            args.extend([search_term, search_term, search_term])
        
        if date_from:
            query += " AND order_date >= ?"
            args.append(date_from)
        
        if date_to:
            query += " AND order_date <= ?"
            args.append(date_to)
        
        query += " ORDER BY order_date DESC"
        
        cursor.execute(query, args)
        orders = cursor.fetchall()
        conn.close()
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(orders, default=json_serializer).encode())
    
    def handle_get_order(self, order_id):
        """Получение конкретного заказа"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if order:
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(order, default=json_serializer).encode())
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Order not found'}).encode())
    
    def handle_get_stats(self):
        """Получение статистики"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Готов к выдаче'")
        ready_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Ожидает выдачи'")
        pending_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Выдан'")
        completed_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Отменен'")
        cancelled_orders = cursor.fetchone()[0]
        
        # Заказы за сегодня
        today = datetime.date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE date(order_date) = ?", (today,))
        today_orders = cursor.fetchone()[0]
        
        # Общая сумма всех заказов
        cursor.execute("SELECT SUM(amount) FROM orders WHERE status != 'Отменен'")
        total_amount = cursor.fetchone()[0] or 0
        
        conn.close()
        
        stats = {
            'total_orders': total_orders,
            'ready_orders': ready_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'today_orders': today_orders,
            'total_amount': float(total_amount)
        }
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def handle_create_order(self):
        """Создание нового заказа"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        order_data = json.loads(post_data.decode())
        
        # Валидация данных
        required_fields = ['order_number', 'client_name', 'phone', 'amount', 'delivery_method', 'pickup_point']
        for field in required_fields:
            if field not in order_data:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Missing field: {field}'}).encode())
                return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (order_number, order_date, client_name, phone, status, amount, delivery_method, pickup_point)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_number'],
            datetime.datetime.now().isoformat(),
            order_data['client_name'],
            order_data['phone'],
            order_data.get('status', 'Ожидает выдачи'),
            order_data['amount'],
            order_data['delivery_method'],
            order_data['pickup_point']
        ))
        
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        
        self.send_response(HTTPStatus.CREATED)
        self.send_header('Content-type', 'application/json')
        self.send_header('Location', f'/api/orders/{order_id}')
        self.end_headers()
        self.wfile.write(json.dumps({'id': order_id, 'message': 'Order created successfully'}).encode())
    
    def handle_issue_order(self):
        """Выдача заказа"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        order_id = data.get('order_id')
        if not order_id:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'order_id is required'}).encode())
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем существование заказа
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Order not found'}).encode())
            return
        
        if order[0] in ['Выдан', 'Отменен']:
            conn.close()
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Order already {order[0].lower()}'}).encode())
            return
        
        cursor.execute("UPDATE orders SET status = 'Выдан' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Order issued successfully'}).encode())
    
    def handle_cancel_order(self):
        """Отмена заказа"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        order_id = data.get('order_id')
        reason = data.get('reason', '')
        
        if not order_id:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'order_id is required'}).encode())
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Order not found'}).encode())
            return
        
        if order[0] in ['Выдан', 'Отменен']:
            conn.close()
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Order already {order[0].lower()}'}).encode())
            return
        
        cursor.execute("UPDATE orders SET status = 'Отменен' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Order cancelled successfully'}).encode())
    
    def handle_update_order_status(self, order_id):
        """Обновление статуса заказа"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        new_status = data.get('status')
        valid_statuses = ['Ожидает выдачи', 'Готов к выдаче', 'Выдан', 'Отменен']
        
        if not new_status or new_status not in valid_statuses:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid status'}).encode())
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Order not found'}).encode())
            return
        
        conn.close()
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Status updated successfully'}).encode())
    
    def handle_delete_order(self, order_id):
        """Удаление заказа (только для отмененных)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Order not found'}).encode())
            return
        
        if order[0] != 'Отменен':
            conn.close()
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Only cancelled orders can be deleted'}).encode())
            return
        
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Order deleted successfully'}).encode())

def json_serializer(obj):
    """Сериализатор для JSON"""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_db_connection():
    """Получение соединения с БД"""
    conn = sqlite3.connect('pvz_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect('pvz_database.db')
    cursor = conn.cursor()
    
    # Создание таблицы заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            order_date TEXT NOT NULL,
            client_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL,
            amount REAL NOT NULL,
            delivery_method TEXT NOT NULL,
            pickup_point TEXT NOT NULL
        )
    ''')
    
    # Добавление тестовых данных если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_orders = [
            ('ORD-001', (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(), 
             'Иванов Иван Иванович', '+7 (999) 123-45-67', 'Готов к выдаче', 3450.50, 'Самовывоз', 'ПВЗ №001'),
            ('ORD-002', (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(), 
             'Петрова Анна Сергеевна', '+7 (999) 765-43-21', 'Ожидает выдачи', 8900.00, 'Курьер', 'ПВЗ №001'),
            ('ORD-003', datetime.datetime.now().isoformat(), 
             'Сидоров Алексей Петрович', '+7 (999) 555-66-77', 'Выдан', 2300.00, 'Самовывоз', 'ПВЗ №001'),
            ('ORD-004', (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(), 
             'Козлова Елена Владимировна', '+7 (999) 111-22-33', 'Отменен', 5600.00, 'Самовывоз', 'ПВЗ №001'),
            ('ORD-005', (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(), 
             'Николаев Дмитрий Сергеевич', '+7 (999) 444-55-66', 'Готов к выдаче', 12500.00, 'Курьер', 'ПВЗ №001'),
            ('ORD-006', datetime.datetime.now().isoformat(), 
             'Соколова Мария Андреевна', '+7 (999) 777-88-99', 'Ожидает выдачи', 4300.50, 'Самовывоз', 'ПВЗ №001')
        ]
        
        cursor.executemany('''
            INSERT INTO orders (order_number, order_date, client_name, phone, status, amount, delivery_method, pickup_point)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_orders)
    
    conn.commit()
    conn.close()
    print("✓ База данных инициализирована")

def run_server():
    """Запуск сервера"""
    try:
        # Инициализация БД
        init_database()
        
        # Создание и запуск сервера
        handler = PVZHandler
        
        # Пытаемся использовать разные адреса если порт занят
        sockets_to_try = [
            (HOST, PORT),
            (HOST, PORT + 1),
            (HOST, PORT + 2),
            ('127.0.0.1', PORT),
            ('0.0.0.0', PORT)
        ]
        
        server = None
        for host, port in sockets_to_try:
            try:
                server = socketserver.TCPServer((host, port), handler)
                HOST = host
                PORT = port
                break
            except OSError:
                continue
        
        if not server:
            print("✗ Не удалось запустить сервер. Все порты заняты.")
            return
        
        print("\n" + "="*50)
        print(f"✓ Сервер ПВЗ запущен!")
        print(f"✓ Адрес: http://{HOST}:{PORT}")
        print(f"✓ API endpoints:")
        print(f"  - GET    /api/orders - список заказов")
        print(f"  - GET    /api/orders/{{id}} - конкретный заказ")
        print(f"  - GET    /api/stats - статистика")
        print(f"  - POST   /api/orders - создать заказ")
        print(f"  - POST   /api/orders/issue - выдать заказ")
        print(f"  - POST   /api/orders/cancel - отменить заказ")
        print(f"  - PUT    /api/orders/{{id}}/status - обновить статус")
        print(f"  - DELETE /api/orders/{{id}} - удалить заказ")
        print(f"✓ База данных: pvz_database.db")
        print("="*50)
        print("Нажмите Ctrl+C для остановки сервера\n")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n⏹ Сервер остановлен")
        if server:
            server.shutdown()
    except Exception as e:
        print(f"✗ Ошибка: {e}")

if __name__ == '__main__':
    run_server()