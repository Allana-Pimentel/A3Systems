from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import socket
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sistema-distribuido-faculdade'

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def send_to_server(command):
    """Envia comando para o servidor socket"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Timeout de 5 segundos
            s.connect((SERVER_HOST, SERVER_PORT))
            s.recv(1024)  # Recebe mensagem de boas-vindas
            s.sendall(command.encode('utf-8'))
            data = s.recv(8192).decode('utf-8')
            return data.strip()
    except ConnectionRefusedError:
        return "ERROR|Servidor não está rodando em localhost:5000"
    except socket.timeout:
        return "ERROR|Timeout ao conectar ao servidor"
    except Exception as e:
        return f"ERROR|{str(e)}"

# -----------------------
# Rotas Web
# -----------------------
@app.route('/')
def index():
    # Pega tarefas do servidor
    response = send_to_server("LIST")
    tasks = []
    
    if "ERROR" not in response and "Nenhum agendamento" not in response:
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line or '-' not in line:
                continue
            try:
                # Formato esperado: "1 - Descrição | 2025-12-03 15:00 | Phone: +5511987654321 | Sent: False"
                parts = line.split('|')
                if len(parts) >= 3:
                    # Parte 0: ID - Descrição
                    id_desc = parts[0].strip()
                    id_str = id_desc.split('-')[0].strip()
                    task_id = int(id_str)
                    description = id_desc.split('-', 1)[1].strip() if '-' in id_desc else ''
                    
                    # Parte 1: Data Hora
                    date_time_str = parts[1].strip()
                    dt_parts = date_time_str.split()
                    date = dt_parts[0] if len(dt_parts) > 0 else ''
                    time = dt_parts[1] if len(dt_parts) > 1 else ''
                    
                    # Parte 2: Telefone
                    phone = parts[2].replace('Phone:', '').strip()
                    
                    # Parte 3 (opcional): Status de envio
                    sent = False
                    if len(parts) > 3:
                        sent = 'True' in parts[3]
                    
                    tasks.append({
                        'id': task_id,
                        'description': description,
                        'date': date,
                        'time': time,
                        'phone': phone,
                        'sent': sent
                    })
            except (ValueError, IndexError) as e:
                print(f"DEBUG: Erro parsing linha: '{line}' - {e}")
                continue
    
    return render_template('index.html', tasks=tasks)

@app.route('/new', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        return add()
    return render_template('form.html')

@app.route('/add', methods=['POST'])
def add():
    try:
        descricao = request.form.get('description', '').strip()
        data = request.form.get('date', '').strip()
        hora = request.form.get('time', '').strip()
        telefone = request.form.get('phone', '').strip()
        
        # Validações
        if not descricao or not data or not hora or not telefone:
            flash("Todos os campos são obrigatórios!")
            return redirect('/new')
        
        # Validação de formato de data/hora
        try:
            datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Formato de data/hora inválido! Use YYYY-MM-DD e HH:MM (24h)")
            return redirect('/new')
        
        # Envia para servidor
        cmd = f"ADD|{descricao}|{data}|{hora}|{telefone}"
        response = send_to_server(cmd)
        
        if "ERROR" in response:
            flash(f"Erro: {response.replace('ERROR|', '')}")
        elif "adicionada" in response.lower():
            flash("✅ Agendamento adicionado com sucesso!")
        else:
            flash(f"Resposta: {response}")
        
        return redirect('/')
    except Exception as e:
        flash(f"Erro: {str(e)}")
        return redirect('/new')

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    cmd = f"REMOVE|{task_id}"
    response = send_to_server(cmd)
    
    if "ERROR" in response:
        flash(f"Erro: {response.replace('ERROR|', '')}")
    elif "sucesso" in response.lower():
        flash("✅ Agendamento removido com sucesso!")
    else:
        flash(f"Resposta: {response}")
    
    return redirect('/')

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    """API para frontend (React/Vue)"""
    response = send_to_server("LIST")
    
    if "ERROR" in response:
        return jsonify({'error': response}), 500
    
    tasks = []
    if "Nenhum agendamento" not in response:
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and '-' in line:
                try:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        id_desc = parts[0].strip()
                        task_id = int(id_desc.split('-')[0].strip())
                        description = id_desc.split('-', 1)[1].strip()
                        
                        date_time_str = parts[1].strip()
                        date = date_time_str.split()[0]
                        time = date_time_str.split()[1] if len(date_time_str.split()) > 1 else ''
                        
                        phone = parts[2].replace('Phone:', '').strip()
                        sent = len(parts) > 3 and 'True' in parts[3]
                        
                        tasks.append({
                            'id': task_id,
                            'description': description,
                            'date': date,
                            'time': time,
                            'phone': phone,
                            'sent': sent
                        })
                except Exception as e:
                    print(f"DEBUG API: {e}")
                    continue
    
    return jsonify({'tasks': tasks, 'count': len(tasks)})

if __name__ == '__main__':
    print("⚠️  Lembre-se de iniciar o servidor primeiro: python servidor.py")
    print("📱 Acesse: http://localhost:5001")
    app.run(debug=True, port=5001)