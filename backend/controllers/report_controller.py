from flask import request, jsonify, send_file
from models import WorkOrder
from models import ManufacturingOrder
from models import WorkCenter
from models.stock_ledger_model import StockLedger
from models.user_model import User
from models.inventory_model import Inventory
from models.product_model import Product
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

def generate_pdf(data, title):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, title)
    y = 700
    for line in data:
        c.drawString(100, y, line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def generate_excel(data, headers):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in data:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def get_operator_report():
    if g.user['role'] != 'Operator':
        return jsonify({'error': 'Unauthorized'}), 403
    user_id = g.user['id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format = request.args.get('format', 'json')

    wos = WorkOrder.find_completed_by_user(user_id)
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        wos = [wo for wo in wos if wo.get('time_spent') and wo['time_spent'] >= start_dt]
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        wos = [wo for wo in wos if wo.get('time_spent') and wo['time_spent'] <= end_dt]

    report_data = [{'wo_id': str(wo['_id']), 'mo_id': wo['mo_id'], 'time_spent': wo.get('time_spent')} for wo in wos]

    if format == 'pdf':
        pdf_data = [f"WO {d['wo_id']}: Time Spent {d['time_spent']}" for d in report_data]
        buffer = generate_pdf(pdf_data, "Operator Completed WOs Report")
        return send_file(buffer, as_attachment=True, download_name='operator_report.pdf', mimetype='application/pdf')
    elif format == 'excel':
        headers = ['WO ID', 'MO ID', 'Time Spent']
        excel_data = [[d['wo_id'], d['mo_id'], d['time_spent']] for d in report_data]
        buffer = generate_excel(excel_data, headers)
        return send_file(buffer, as_attachment=True, download_name='operator_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return jsonify(report_data), 200

def get_manager_report():
    if g.user['role'] != 'Manufacturing Manager':
        return jsonify({'error': 'Unauthorized'}), 403
    start_date = datetime.fromisoformat(request.args.get('start_date', (datetime.now() - timedelta(days=30)).isoformat()))
    end_date = datetime.fromisoformat(request.args.get('end_date', datetime.now().isoformat()))
    format = request.args.get('format', 'json')

    # Throughput: completed MOs quantity per day
    mos = ManufacturingOrder.find_completed_between(start_date, end_date)
    throughput = sum(mo['quantity'] for mo in mos) / ((end_date - start_date).days + 1) if mos else 0

    # Delays: overdue MOs
    delays = ManufacturingOrder.count_overdue()

    # Resource utilization: avg time_spent / planned_duration for WOs
    wos = WorkOrder.find_completed_between(start_date, end_date)
    utilization = sum(wo['time_spent'] / wo['planned_duration'] for wo in wos if wo.get('planned_duration')) / len(wos) * 100 if wos else 0

    report_data = {'throughput': throughput, 'delays': delays, 'utilization': f'{utilization:.2f}%'}

    if format == 'pdf':
        pdf_data = [f"Throughput: {report_data['throughput']}", f"Delays: {report_data['delays']}", f"Utilization: {report_data['utilization']}"]
        buffer = generate_pdf(pdf_data, "Manager Production Report")
        return send_file(buffer, as_attachment=True, download_name='manager_report.pdf', mimetype='application/pdf')
    elif format == 'excel':
        headers = ['Metric', 'Value']
        excel_data = [['Throughput', report_data['throughput']], ['Delays', report_data['delays']], ['Utilization', report_data['utilization']]]
        buffer = generate_excel(excel_data, headers)
        return send_file(buffer, as_attachment=True, download_name='manager_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return jsonify(report_data), 200

def get_admin_report():
    if g.user['role'] != 'Administrator':
        return jsonify({'error': 'Unauthorized'}), 403
    format = request.args.get('format', 'json')

    total_mos = ManufacturingOrder.count_all()
    total_wos = WorkOrder.count_all()
    total_users = User.count_all()
    total_inventory = sum(inv['stock_quantity'] for inv in Inventory.find_all())

    report_data = {'total_mos': total_mos, 'total_wos': total_wos, 'total_users': total_users, 'total_inventory': total_inventory}

    if format == 'pdf':
        pdf_data = [f"Total MOs: {report_data['total_mos']}", f"Total WOs: {report_data['total_wos']}", f"Total Users: {report_data['total_users']}", f"Total Inventory: {report_data['total_inventory']}"]
        buffer = generate_pdf(pdf_data, "Admin System Report")
        return send_file(buffer, as_attachment=True, download_name='admin_report.pdf', mimetype='application/pdf')
    elif format == 'excel':
        headers = ['Metric', 'Value']
        excel_data = [['Total MOs', report_data['total_mos']], ['Total WOs', report_data['total_wos']], ['Total Users', report_data['total_users']], ['Total Inventory', report_data['total_inventory']]]
        buffer = generate_excel(excel_data, headers)
        return send_file(buffer, as_attachment=True, download_name='admin_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return jsonify(report_data), 200

def get_inventory_report():
    if g.user['role'] != 'Inventory Manager':
        return jsonify({'error': 'Unauthorized'}), 403
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format = request.args.get('format', 'json')

    report_data = StockLedger.get_usage_by_product(start_date, end_date)

    if format == 'pdf':
        pdf_data = [f"{d['product']}: Usage {d['usage']}" for d in report_data]
        buffer = generate_pdf(pdf_data, "Inventory Stock Usage Report")
        return send_file(buffer, as_attachment=True, download_name='inventory_report.pdf', mimetype='application/pdf')
    elif format == 'excel':
        headers = ['Product', 'Usage']
        excel_data = [[d['product'], d['usage']] for d in report_data]
        buffer = generate_excel(excel_data, headers)
        return send_file(buffer, as_attachment=True, download_name='inventory_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return jsonify(report_data), 200