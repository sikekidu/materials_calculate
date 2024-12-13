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
    query = "SELECT * FROM shield WHERE shield_type = %s"
    cursor.execute(query, (shield_type,))
    shield_data = cursor.fetchall()

    # 计算材料和设备需求（示例逻辑）
    materials = {}
    for row in shield_data:
        # 假设row包含材料和设备需求信息
        # 确保 row[3] (shield_diameter) 和 row[4] (tunneling_distance) 是数字类型
        try:
            shield_diameter = float(row[3])
            tunneling_distance = float(row[4])
            materials[row[5]] = shield_diameter * float(distance)  # 示例计算
        except ValueError:
            materials[row[5]] = "Invalid data type for calculation"

    cursor.close()
    conn.close()

    return jsonify({'project_name': project_name, 'materials': materials})

if __name__ == '__main__':
    app.run(debug=True)
