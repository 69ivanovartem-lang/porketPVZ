import urllib.request
import urllib.parse
import json
import sys

class PVZClient:
    def __init__(self, host='localhost', port=8000):
        self.base_url = f'http://{host}:{port}'
    
    def make_request(self, method, endpoint, data=None):
        """Выполнение HTTP запроса"""
        url = f'{self.base_url}{endpoint}'
        
        request = urllib.request.Request(url, method=method)
        
        if data:
            data_bytes = json.dumps(data).encode('utf-8')
            request.add_header('Content-Type', 'application/json')
            request.data = data_bytes
        
        try:
            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            print(f"HTTP Error {e.code}: {error_data}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_orders(self, status=None, search=None):
        """Получение списка заказов"""
        params = {}
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        
        query_string = urllib.parse.urlencode(params)
        endpoint = f'/api/orders?{query_string}' if params else '/api/orders'
        
        return self.make_request('GET', endpoint)
    
    def get_order(self, order_id):
        """Получение конкретного заказа"""
        return self.make_request('GET', f'/api/orders/{order_id}')
    
    def get_stats(self):
        """Получение статистики"""
        return self.make_request('GET', '/api/stats')
    
    def create_order(self, order_data):
        """Создание заказа"""
        return self.make_request('POST', '/api/orders', order_data)
    
    def issue_order(self, order_id):
        """Выдача заказа"""
        return self.make_request('POST', '/api/orders/issue', {'order_id': order_id})
    
    def cancel_order(self, order_id, reason=''):
        """Отмена заказа"""
        return self.make_request('POST', '/api/orders/cancel', {'order_id': order_id, 'reason': reason})
    
    def update_status(self, order_id, status):
        """Обновление статуса"""
        return self.make_request('PUT', f'/api/orders/{order_id}/status', {'status': status})
    
    def delete_order(self, order_id):
        """Удаление заказа"""
        return self.make_request('DELETE', f'/api/orders/{order_id}')

def print_orders(orders):
    """Вывод заказов в консоль"""
    if not orders:
        print("Заказы не найдены")
        return
    
    print("\n" + "="*100)
    print(f"{'№':<4} {'Номер заказа':<12} {'Дата':<12} {'Клиент':<25} {'Статус':<15} {'Сумма':<10}")
    print("-"*100)
    
    for i, order in enumerate(orders, 1):
        print(f"{i:<4} {order['order_number']:<12} {order['order_date'][:10]:<12} "
              f"{order['client_name'][:24]:<25} {order['status']:<15} {order['amount']:<10.2f}")
    print("="*100)

def main():
    """Пример использования клиента"""
    client = PVZClient()
    
    print("📦 Тестирование API ПВЗ")
    print("="*50)
    
    # Получение статистики
    print("\n📊 Статистика:")
    stats = client.get_stats()
    if stats:
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Получение всех заказов
    print("\n📋 Все заказы:")
    orders = client.get_orders()
    print_orders(orders)
    
    # Фильтрация по статусу
    print("\n🔍 Заказы со статусом 'Готов к выдаче':")
    ready_orders = client.get_orders(status='Готов к выдаче')
    print_orders(ready_orders)
    
    # Создание нового заказа
    print("\n➕ Создание нового заказа:")
    new_order = {
        'order_number': 'ORD-007',
        'client_name': 'Тестовый Клиент',
        'phone': '+7 (999) 888-77-66',
        'amount': 9999.99,
        'delivery_method': 'Самовывоз',
        'pickup_point': 'ПВЗ №001'
    }
    result = client.create_order(new_order)
    if result:
        print(f"✓ Заказ создан: {result}")
    
    # Поиск заказа
    print("\n🔎 Поиск заказа 'ORD-001':")
    found_orders = client.get_orders(search='ORD-001')
    print_orders(found_orders)
    
    # Выдача заказа
    if found_orders:
        order_id = found_orders[0]['id']
        print(f"\n📤 Выдача заказа ID {order_id}:")
        result = client.issue_order(order_id)
        if result:
            print(f"✓ {result['message']}")

if __name__ == '__main__':
    main()