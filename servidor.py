# servidor.py
import socket
import threading
import json
import os
from datetime import datetime, date, time as dtime
import time
import pywhatkit as kit

HOST = '0.0.0.0'
PORT = 5000

TASKS_FILE = 'tasks.json'
CHECK_INTERVAL_SECONDS = 30  # checar lembretes a cada 30s

lock = threading.Lock()

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def next_id(tasks):
    return (max([t['id'] for t in tasks]) + 1) if tasks else 1

def add_task(description, date_str, time_str, phone):
    with lock:
        tasks = load_tasks()
        tid = next_id(tasks)
        task = {
            'id': tid,
            'description': description,
            'date': date_str,   # 'YYYY-MM-DD'
            'time': time_str,   # 'HH:MM'
            'phone': phone,
            'sent': False,
            'created_at': datetime.now().isoformat()
        }
        tasks.append(task)
        save_tasks(tasks)
    return task

def list_tasks():
    with lock:
        return load_tasks()

def remove_task(task_id):
    with lock:
        tasks = load_tasks()
        new_tasks = [t for t in tasks if t['id'] != task_id]
        changed = len(new_tasks) != len(tasks)
        if changed:
            save_tasks(new_tasks)
        return changed

def edit_task(task_id, description, date_str, time_str, phone):
    with lock:
        tasks = load_tasks()
        found = False
        for t in tasks:
            if t['id'] == task_id:
                t['description'] = description
                t['date'] = date_str
                t['time'] = time_str
                t['phone'] = phone
                t['sent'] = False  # reset sent when edit
                t['updated_at'] = datetime.now().isoformat()
                found = True
                break
        if found:
            save_tasks(tasks)
        return found

def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def send_whatsapp_message(phone, message):
    """
    Usa pywhatkit para enviar mensagem via WhatsApp Web.
    Requisitos: navegador com WhatsApp Web logado.
    """
    try:
        # wait_time dá tempo para o browser abrir; tab_close fecha aba depois
        kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True, close_time=3)
        return True, None
    except Exception as e:
        return False, str(e)

def reminder_checker():
    """Thread que verifica tarefas e envia lembretes na data/hora."""
    while True:
        try:
            now = datetime.now()
            with lock:
                tasks = load_tasks()
            for task in tasks:
                if task.get('sent'):
                    continue
                try:
                    target_dt = parse_datetime(task['date'], task['time'])
                except Exception:
                    # formato inválido - marcar erro e continuar
                    with lock:
                        for t in tasks:
                            if t['id'] == task['id']:
                                t['error'] = "Formato de data/hora inválido"
                                save_tasks(tasks)
                    continue

                # enviar se target <= now
                if target_dt <= now:
                    phone = task.get('phone')
                    desc = task.get('description')
                    message = f"📅 Lembrete: {task['date']} {task['time']}: \"{desc}\""
                    print(f"[{datetime.now().isoformat()}] Enviando lembrete ID {task['id']} para {phone}")
                    ok, err = send_whatsapp_message(phone, message)
                    with lock:
                        tasks = load_tasks()
                        for t in tasks:
                            if t['id'] == task['id']:
                                t['sent'] = ok
                                if not ok:
                                    t['error'] = err
                                else:
                                    t['sent_at'] = datetime.now().isoformat()
                        save_tasks(tasks)
                    if ok:
                        print(f"[{datetime.now().isoformat()}] Lembrete enviado com sucesso para {phone}")
                    else:
                        print(f"[{datetime.now().isoformat()}] Erro ao enviar para {phone}: {err}")
            time.sleep(CHECK_INTERVAL_SECONDS)
        except Exception as ex:
            print("Erro no reminder_checker:", ex)
            time.sleep(10)

def handle_client(conn, addr):
    with conn:
        print(f"Conexão de {addr}")
        welcome = (
            "Conectado ao servidor de tarefas.\n"
            "Comandos:\n"
            "ADD|Descrição|YYYY-MM-DD|HH:MM|+55DDDNÚMERO\n"
            "LIST\n"
            "REMOVE|ID\n"
            "EDIT|ID|Descrição|YYYY-MM-DD|HH:MM|+55DDDNÚMERO\n"
            "EXIT\n"
        )
        conn.sendall(welcome.encode('utf-8'))
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8').strip()
                if not text:
                    continue
                parts = text.split('|')
                cmd = parts[0].upper()
                if cmd == 'ADD' and len(parts) == 5:
                    desc = parts[1].strip()
                    date_str = parts[2].strip()
                    time_str = parts[3].strip()
                    phone = parts[4].strip()
                    # validações simples
                    try:
                        parse_datetime(date_str, time_str)
                        t = add_task(desc, date_str, time_str, phone)
                        conn.sendall(f"Tarefa adicionada: ID {t['id']}\n".encode('utf-8'))
                    except ValueError:
                        conn.sendall("Formato de data/hora inválido. Use YYYY-MM-DD e HH:MM (24h)\n".encode('utf-8'))
                elif cmd == 'LIST':
                    tasks = list_tasks()
                    if not tasks:
                        conn.sendall("Nenhuma tarefa cadastrada.\n".encode('utf-8'))
                    else:
                        out_lines = []
                        for t in tasks:
                            out_lines.append(
                                f"{t['id']} - {t['description']} | {t['date']} {t['time']} | Phone: {t['phone']} | Sent: {t.get('sent', False)}"
                            )
                        out = "\n".join(out_lines) + "\n"
                        conn.sendall(out.encode('utf-8'))
                elif cmd == 'REMOVE' and len(parts) == 2:
                    try:
                        tid = int(parts[1])
                        ok = remove_task(tid)
                        if ok:
                            conn.sendall("Tarefa removida com sucesso.\n".encode('utf-8'))
                        else:
                            conn.sendall("ID não encontrado.\n".encode('utf-8'))
                    except ValueError:
                        conn.sendall("ID inválido.\n".encode('utf-8'))
                elif cmd == 'EDIT' and len(parts) == 6:
                    try:
                        tid = int(parts[1])
                        desc = parts[2].strip()
                        date_str = parts[3].strip()
                        time_str = parts[4].strip()
                        phone = parts[5].strip()
                        # valida data/hora
                        try:
                            parse_datetime(date_str, time_str)
                        except ValueError:
                            conn.sendall("Formato de data/hora inválido. Use YYYY-MM-DD e HH:MM (24h)\n".encode('utf-8'))
                            continue
                        ok = edit_task(tid, desc, date_str, time_str, phone)
                        if ok:
                            conn.sendall("Tarefa editada com sucesso.\n".encode('utf-8'))
                        else:
                            conn.sendall("ID não encontrado.\n".encode('utf-8'))
                    except ValueError:
                        conn.sendall("ID inválido.\n".encode('utf-8'))
                elif cmd == 'EXIT':
                    conn.sendall("Fechando conexão. Tchau!\n".encode('utf-8'))
                    break
                else:
                    conn.sendall("Comando inválido.\n".encode('utf-8'))
        except ConnectionResetError:
            print(f"Conexão com {addr} perdida.")
        print(f"Conexão encerrada: {addr}")

def main():
    checker_thread = threading.Thread(target=reminder_checker, daemon=True)
    checker_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor ouvindo em {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == '__main__':
    main()
