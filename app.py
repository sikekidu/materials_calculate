from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

app = Flask(__name__)

# 从环境变量中获取数据库连接配置
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_quote', methods=['POST'])
def generate_quote():
    project_name = request.form['project_name']
    diameter = request.form['diameter']
    distance = request.form['distance']
    shield_type = request.form['shield_type']

    # 连接到数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 根据盾构机类型查询数据
    query = "SELECT item_name, item_code, unit, quantity, cost_price, cost_amount, reference_price, reference_amount FROM shield WHERE shield_type = %s"
    cursor.execute(query, (shield_type,))
    shield_data = cursor.fetchall()

    # 直接返回与输入的盾构机类型一致的所有数据
    results = []
    for row in shield_data:
        results.append(row)

    cursor.close()
    conn.close()

    print(f"返回的数据: {results}")  # 添加调试信息
    return jsonify({'project_name': project_name, 'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
