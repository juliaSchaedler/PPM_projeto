import threading
import time
import random
import json
import pika
import mysql.connector
from mysql.connector import Error
from colorama import Fore, Style, init

init(autoreset=True)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'rabbitmq_service'
MYSQL_HOST = 'mysql_service'
MYSQL_USER = 'app_user'  # Corrigido para o valor correto
MYSQL_PASSWORD = 'app_password'  # Corrigido para o valor correto
MYSQL_DB = 'promo_app'  # Corrigido para o valor correto

# Conexão com RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        break
    except pika.exceptions.AMQPConnectionError:
        print("Aguardando RabbitMQ iniciar...")
        time.sleep(5)

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Configuração inicial
estoque = {
    'produtoA': 100,
    'produtoB': 50,
    'produtoC': 200,
    'produtoD': 30,
    'produtoE': 100
}
locks_por_produto = {produto: threading.Lock() for produto in estoque.keys()}

channel.queue_declare(queue='fila_de_pedidos')
channel.queue_declare(queue='fila_de_processados')

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return conexao
    except Error as e:
        print(f"{Fore.RED}Erro ao conectar no banco de dados: {e}")
        return None

# Função para criar as tabelas caso não existam
def criar_tabelas():
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto VARCHAR(255),
                    quantidade INT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estoque (
                    produto VARCHAR(255) PRIMARY KEY,
                    quantidade INT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS erros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto VARCHAR(255),
                    mensagem TEXT
                )
            """)
            conexao.commit()
        except Error as e:
            print(f"{Fore.RED}Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            conexao.close()

# Chama a função de criação das tabelas
criar_tabelas()

# Cliente (Produtor)
def cliente(num_pedidos):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    try:
        for _ in range(num_pedidos):
            produto = random.choice(list(estoque.keys()))
            quantidade = random.randint(1, 10)
            pedido = {'produto': produto, 'quantidade': quantidade}
            pedido_json = json.dumps(pedido)

            print(f"{Fore.GREEN}Cliente gerou o pedido: {pedido_json}")
            channel.basic_publish(exchange='', routing_key='fila_de_pedidos', body=pedido_json)
            time.sleep(random.uniform(0.1, 0.5))
    finally:
        connection.close()

# Processador de Estoque (Consumidor)
def processador_de_estoque():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        try:
            pedido = json.loads(body)
            produto = pedido['produto']
            quantidade = pedido['quantidade']

            with locks_por_produto[produto]:
                conexao = conectar_banco()
                if conexao:
                    cursor = conexao.cursor()
                    try:
                        # Verifica estoque
                        if estoque[produto] >= quantidade:
                            estoque[produto] -= quantidade
                            print(f"{Fore.BLUE}Pedido processado: {pedido}. Estoque atualizado: {estoque[produto]} unidades restantes.")

                            # Atualiza banco
                            cursor.execute("INSERT INTO pedidos (produto, quantidade) VALUES (%s, %s)", (produto, quantidade))
                            cursor.execute("UPDATE estoque SET quantidade = %s WHERE produto = %s", (estoque[produto], produto))
                            conexao.commit()

                            # Publica pedido processado
                            channel.basic_publish(exchange='', routing_key='fila_de_processados', body=json.dumps(pedido))
                        else:
                            print(f"{Fore.RED}Estoque insuficiente para {produto}. Pedido não processado.")
                            cursor.execute("INSERT INTO erros (produto, mensagem) VALUES (%s, %s)", (produto, 'Estoque insuficiente'))
                            conexao.commit()
                    except Error as e:
                        print(f"{Fore.RED}Erro no banco de dados: {e}")
                    finally:
                        cursor.close()
                        conexao.close()

            # Confirma que a mensagem foi processada
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"{Fore.RED}Erro no processamento do pedido: {e}")

    # Limitar o número de mensagens consumidas
    mensagens_consumidas = 0
    while mensagens_consumidas < 50:  # Limite de mensagens consumidas
        channel.basic_consume(queue='fila_de_pedidos', on_message_callback=callback, auto_ack=False)
        channel.start_consuming()
        mensagens_consumidas += 1

# Configuração de threads
num_clientes = 3
num_pedidos_por_cliente = 10

clientes = [threading.Thread(target=cliente, args=(num_pedidos_por_cliente,)) for _ in range(num_clientes)]
processadores = [threading.Thread(target=processador_de_estoque) for _ in range(5)]  # Aumentei o número de processadores

# Inicia threads
for t in clientes + processadores:
    t.start()

# Aguarda conclusão
for t in clientes + processadores:
    t.join()

print(f"{Fore.CYAN}{Style.BRIGHT}Estoque Final:")
for produto, quantidade in estoque.items():
    print(f"{Fore.CYAN}Produto: {produto} | {quantidade} unidades restantes")
