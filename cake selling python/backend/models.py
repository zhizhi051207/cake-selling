import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='../data/cake_shop.db'):
        """初始化数据库"""
        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建蛋糕表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                image_url TEXT,
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建订单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建订单项表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                cake_id INTEGER NOT NULL,
                cake_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (cake_id) REFERENCES cakes (id)
            )
        ''')

        # 插入示例数据
        cursor.execute('SELECT COUNT(*) FROM cakes')
        if cursor.fetchone()[0] == 0:
            sample_cakes = [
                ('经典巧克力蛋糕', '浓郁的巧克力口感，层层叠叠的美味', 88.0, '巧克力系列', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587', 20),
                ('草莓奶油蛋糕', '新鲜草莓搭配轻盈奶油，清新怡人', 78.0, '水果系列', 'https://images.unsplash.com/photo-1565958011703-44f9829ba187', 15),
                ('提拉米苏', '意式经典，咖啡与芝士的完美融合', 98.0, '芝士系列', 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9', 10),
                ('抹茶慕斯蛋糕', '清香抹茶，入口即化的慕斯口感', 85.0, '抹茶系列', 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e', 12),
                ('芒果千层蛋糕', '层层薄饼，满满芒果果肉', 92.0, '水果系列', 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3', 18),
                ('黑森林蛋糕', '德式经典，樱桃与巧克力的绝配', 95.0, '巧克力系列', 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62', 8),
                ('红丝绒蛋糕', '独特的红色外观，柔软细腻的口感', 88.0, '芝士系列', 'https://images.unsplash.com/photo-1586788680434-30d324b2d46f', 14),
                ('榴莲千层蛋糕', '榴莲爱好者的天堂，浓郁榴莲香', 108.0, '水果系列', 'https://images.unsplash.com/photo-1621303837174-89787a7d4729', 6),
            ]

            cursor.executemany('''
                INSERT INTO cakes (name, description, price, category, image_url, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_cakes)

        conn.commit()
        conn.close()

    # 蛋糕相关方法
    def get_all_cakes(self):
        """获取所有蛋糕"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cakes ORDER BY created_at DESC')
        cakes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cakes

    def get_cake(self, cake_id):
        """获取单个蛋糕"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cakes WHERE id = ?', (cake_id,))
        cake = cursor.fetchone()
        conn.close()
        return dict(cake) if cake else None

    def add_cake(self, name, description, price, category, image_url='', stock=0):
        """添加蛋糕"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cakes (name, description, price, category, image_url, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, price, category, image_url, stock))
        cake_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cake_id

    def update_cake(self, cake_id, name=None, description=None, price=None,
                    category=None, image_url=None, stock=None):
        """更新蛋糕信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if price is not None:
            updates.append('price = ?')
            params.append(price)
        if category is not None:
            updates.append('category = ?')
            params.append(category)
        if image_url is not None:
            updates.append('image_url = ?')
            params.append(image_url)
        if stock is not None:
            updates.append('stock = ?')
            params.append(stock)

        if not updates:
            conn.close()
            return False

        params.append(cake_id)
        query = f"UPDATE cakes SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_cake(self, cake_id):
        """删除蛋糕"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cakes WHERE id = ?', (cake_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # 订单相关方法
    def create_order(self, customer_name, phone, address, total, items):
        """创建订单"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建订单
        cursor.execute('''
            INSERT INTO orders (customer_name, phone, address, total)
            VALUES (?, ?, ?, ?)
        ''', (customer_name, phone, address, total))

        order_id = cursor.lastrowid

        # 添加订单项
        for item in items:
            cursor.execute('''
                INSERT INTO order_items (order_id, cake_id, cake_name, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item['cake_id'], item['name'], item['price'], item['quantity']))

            # 更新库存
            cursor.execute('''
                UPDATE cakes SET stock = stock - ? WHERE id = ?
            ''', (item['quantity'], item['cake_id']))

        conn.commit()
        conn.close()
        return order_id

    def get_all_orders(self):
        """获取所有订单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        orders = []

        for row in cursor.fetchall():
            order = dict(row)
            # 获取订单项
            cursor.execute('''
                SELECT * FROM order_items WHERE order_id = ?
            ''', (order['id'],))
            order['items'] = [dict(item_row) for item_row in cursor.fetchall()]
            orders.append(order)

        conn.close()
        return orders

    def get_order(self, order_id):
        """获取订单详情"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order_row = cursor.fetchone()

        if not order_row:
            conn.close()
            return None

        order = dict(order_row)

        # 获取订单项
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        order['items'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return order

    def update_order_status(self, order_id, status):
        """更新订单状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_statistics(self):
        """获取统计数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 总销售额
        cursor.execute('SELECT COALESCE(SUM(total), 0) FROM orders')
        total_sales = cursor.fetchone()[0]

        # 订单数量
        cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = cursor.fetchone()[0]

        # 待处理订单
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"')
        pending_orders = cursor.fetchone()[0]

        # 蛋糕种类
        cursor.execute('SELECT COUNT(*) FROM cakes')
        total_cakes = cursor.fetchone()[0]

        # 热门蛋糕
        cursor.execute('''
            SELECT cake_name, SUM(quantity) as total_sold
            FROM order_items
            GROUP BY cake_name
            ORDER BY total_sold DESC
            LIMIT 5
        ''')
        popular_cakes = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_cakes': total_cakes,
            'popular_cakes': popular_cakes
        }
