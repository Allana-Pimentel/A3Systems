import socket
from datetime import datetime

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def menu_principal():
    print("\n=== MENU ===")
    print("1 - Adicionar tarefa")
    print("2 - Listar tarefas")
    print("3 - Editar tarefa")
    print("4 - Remover tarefa")
    print("5 - Sair")
    print("===============")

def criar_tarefa():
    print("\n--- Criar nova tarefa ---")
    descricao = input("Descrição: ").strip()
    data = input("Data (YYYY-MM-DD): ").strip()
    hora = input("Hora (HH:MM 24h): ").strip()
    telefone = input("Telefone (+55DDDNÚMERO): ").strip()
    
    # validação rápida
    try:
        datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        print("❌ Data ou hora inválida!")
        return None
    
    return f"ADD|{descricao}|{data}|{hora}|{telefone}"

def editar_tarefa():
    print("\n--- Editar tarefa ---")
    task_id = input("ID da tarefa: ").strip()
    descricao = input("Nova descrição: ").strip()
    data = input("Nova data (YYYY-MM-DD): ").strip()
    hora = input("Nova hora (HH:MM 24h): ").strip()
    telefone = input("Novo telefone (+55DDDNÚMERO): ").strip()

    return f"EDIT|{task_id}|{descricao}|{data}|{hora}|{telefone}"

def remover_tarefa():
    print("\n--- Remover tarefa ---")
    task_id = input("ID da tarefa: ").strip()
    return f"REMOVE|{task_id}"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        welcome = s.recv(4096).decode('utf-8')
        print(welcome)

        while True:
            menu_principal()
            opcao = input("Escolha: ").strip()

            if opcao == '1':
                cmd = criar_tarefa()
                if not cmd:
                    continue

            elif opcao == '2':
                cmd = "LIST"

            elif opcao == '3':
                cmd = editar_tarefa()

            elif opcao == '4':
                cmd = remover_tarefa()

            elif opcao == '5':
                cmd = "EXIT"

            else:
                print("❌ Opção inválida!")
                continue

            s.sendall(cmd.encode('utf-8'))
            data = s.recv(8192).decode('utf-8')
            print("\n" + data)

            if cmd == "EXIT":
                print("Encerrando cliente...")
                break

if __name__ == '__main__':
    main()
