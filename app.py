from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from fpdf import FPDF
import io
import pdfkit  # 确保导入 pdfkit

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

    return jsonify({'project_name': project_name, 'results': results})

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    project_name = data['project_name']
    diameter = data['diameter']
    distance = data['distance']
    shield_type = data['shield_type']
    results = data['results']

    # 计算合计
    total_amount = sum(float(item[7]) for item in results)  # 假设第7列是参考金额

    # 使用模板生成 PDF
    pdf_html = render_template('pdf_template.html', project_name=project_name, diameter=diameter, distance=distance, shield_type=shield_type, results=results, total_amount=total_amount)

    # 生成 PDF
    pdf = pdfkit.from_string(pdf_html, False)
    return send_file(io.BytesIO(pdf), download_name='quote.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
