# 📋 Sistema Distribuído de Gerenciamento de Tarefas com Lembretes via WhatsApp

Sistema distribuído em Python que permite gerenciar tarefas e receber lembretes automáticos via WhatsApp Web.

## 📋 Pré-requisitos

- Python 3.8+
- Navegador com WhatsApp Web logado (Chrome, Edge ou Firefox)
- Conexão com a Internet

## 🚀 Instalação

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Fazer login no WhatsApp Web:**
   - Abra seu navegador padrão
   - Acesse https://web.whatsapp.com
   - Faça login com seu celular
   - Mantenha a aba aberta para que o PyWhatKit funcione

## ▶️ Como Executar

### Opção 1: Cliente via Socket (Recomendado)

**Terminal 1 - Iniciar Servidor:**
```bash
python servidor.py
```
Aguarde a mensagem: `Servidor ouvindo em 0.0.0.0:5001`

**Terminal 2 - Conectar Cliente CLI:**
```bash
python client.py
```

### Opção 2: Interface Web (Experimental)

**Terminal 1 - Iniciar Servidor:**
```bash
python servidor.py
```

**Terminal 2 - Iniciar Web App:**
```bash
python web_app.py
```
Acesse: http://localhost:5000

## 📝 Comandos Disponíveis (Cliente CLI)

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| ADD | Adiciona nova tarefa | `ADD\|Reunião\|2025-12-03\|15:00\|+5511987654321` |
| LIST | Lista todas as tarefas | `LIST` |
| REMOVE | Remove tarefa por ID | `REMOVE\|5` |
| EDIT | Edita tarefa existente | `EDIT\|3\|Nova desc\|2025-12-04\|10:00\|+5511987654321` |
| EXIT | Encerra conexão | `EXIT` |

## 🔧 Formato de Dados

- **Data:** YYYY-MM-DD (ex: 2025-12-03)
- **Hora:** HH:MM em formato 24h (ex: 15:30)
- **Telefone:** +55DDD9NÚMERO (ex: +5511987654321)

## 📌 Notas Importantes

✅ O servidor verifica tarefas a cada 30 segundos  
✅ Lembretes são enviados automaticamente quando a hora chega  
✅ Tarefas são salvas em `tasks.json` (persistência local)  
⚠️ O navegador abrirá automaticamente para enviar mensagens WhatsApp  
⚠️ Manter o navegador aberto enquanto o servidor estiver rodando  

## 🗂️ Estrutura do Projeto

```
a3systems/
├── servidor.py           # Servidor Socket (core do sistema)
├── client.py             # Cliente CLI
├── web_app.py            # Interface Web (Flask)
├── templates/
│   ├── base.html
│   ├── form.html
│   └── index.html
├── requirements.txt      # Dependências Python
├── tasks.json            # Persistência de tarefas
└── DOCUMENTACAO.md       # Documentação completa
```

