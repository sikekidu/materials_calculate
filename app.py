from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from fpdf import FPDF
import io

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

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 添加标题
    pdf.set_font("Arial", size=20, style="B")
    pdf.cell(200, 10, txt="设备维保事业部", ln=True, align='C')

    # 添加项目信息
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"项目名称: {project_name}", ln=True)
    pdf.cell(200, 10, txt=f"盾构机直径: {diameter}", ln=True)
    pdf.cell(200, 10, txt=f"掘进里程: {distance}", ln=True)
    pdf.cell(200, 10, txt=f"盾构机类型: {shield_type}", ln=True)

    # 添加表格
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(200, 10, txt="序号 材料名称 单位 数量 参考价格 参考金额", ln=True, align='C')

    # 添加表格数据
    pdf.set_font("Arial", size=12)
    for index, row in enumerate(results, start=1):
        if index % 20 == 0:  # 每20行添加一页
            pdf.add_page()
            pdf.set_font("Arial", size=12, style="B")
            pdf.cell(200, 10, txt="序号 材料名称 单位 数量 参考价格 参考金额", ln=True, align='C')
        row_data = [
            str(index),  # 序号
            row[0],       # 材料名称
            row[2],       # 单位
            row[3],       # 数量
            row[6],       # 参考价格
            row[7]        # 参考金额
        ]
        pdf.cell(200, 10, txt=" ".join(row_data), ln=True)

    # 保存 PDF 到内存
    pdf_data = io.BytesIO()
    pdf.output(pdf_data)
    pdf_data.seek(0)
    return send_file(pdf_data, as_attachment=True, download_name='quote.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
