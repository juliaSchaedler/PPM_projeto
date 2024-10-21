import threading
import queue
import time
import random
import json
from colorama import Fore, Style, init
from prometheus_client import start_http_server, Counter, Gauge
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# Estoque inicial
estoque = {
    'produtoA': 100,
    'produtoB': 50,
    'produtoC': 200,
    'produtoD': 30,
    'produtoE': 100
}

# Criação de locks individuais para cada produto
locks_por_produto = {produto: threading.Lock() for produto in estoque.keys()}

# Fila de pedidos e fila de pedidos processados
fila_de_pedidos = queue.Queue()
fila_de_processados = queue.Queue()

# Inicializa as métricas de observabilidade
pedidos_processados = Counter('pedidos_processados_total', 'Total de pedidos processados')
pedidos_invalidos = Counter('pedidos_invalidos_total', 'Total de pedidos rejeitados por falta de estoque')
estoque_atual = Gauge('estoque_produto', 'Quantidade em estoque', ['produto'])

# Inicia o servidor Prometheus para coletar as métricas na porta 8000
start_http_server(8000)

# Função para atualizar métricas do estoque
def atualizar_metricas_estoque():
    for produto, quantidade in estoque.items():
        estoque_atual.labels(produto).set(quantidade)

# Função do cliente (gerando pedidos aleatórios)
def cliente(num_pedidos):
    for i in range(num_pedidos):
        produto = random.choice(list(estoque.keys()))
        quantidade = random.randint(1, 10)
        pedido = {'produto': produto, 'quantidade': quantidade}
        
        # Converte o pedido para JSON
        pedido_json = json.dumps(pedido)
        
        print(f"{Fore.GREEN}Cliente gerou o pedido: {pedido_json}")
        fila_de_pedidos.put(pedido_json)  # Adiciona o pedido à fila
        time.sleep(random.uniform(0.1, 0.5))

# Função para processar os pedidos do estoque
def processador_de_estoque():
    while True:
        try:
            # Pega o pedido da fila (formato JSON) e converte de volta para dicionário
            pedido_json = fila_de_pedidos.get(timeout=2)
            pedido = json.loads(pedido_json)
            produto = pedido['produto']
            quantidade = pedido['quantidade']

            # Seção crítica específica para o produto
            with locks_por_produto[produto]:
                if estoque[produto] >= quantidade:
                    estoque[produto] -= quantidade
                    print(f"{Fore.BLUE}Pedido processado: {pedido}. Estoque atualizado: {estoque[produto]} unidades restantes.")
                    
                    # Adiciona o pedido processado na fila de saída
                    fila_de_processados.put(json.dumps(pedido))
                    pedidos_processados.inc()  # Incrementa a métrica de pedidos processados
                else:
                    print(f"{Fore.RED}Estoque insuficiente para {produto}. Pedido não processado.")
                    pedidos_invalidos.inc()  # Incrementa a métrica de pedidos inválidos
            
            # Atualiza as métricas do estoque
            atualizar_metricas_estoque()
            fila_de_pedidos.task_done()
            
        except queue.Empty:
            print(f"{Fore.YELLOW}Nenhum pedido na fila.")
            break

# Configuração das threads dos clientes
num_clientes = 3
num_pedidos_por_cliente = 10

# Iniciar clientes
clientes = []
for i in range(num_clientes):
    t = threading.Thread(target=cliente, args=(num_pedidos_por_cliente,))
    clientes.append(t)
    t.start()

# Usar ThreadPoolExecutor para gerenciar processadores de estoque (balanceamento de carga)
num_processadores = 3
with ThreadPoolExecutor(max_workers=num_processadores) as executor:
    for _ in range(num_processadores):
        executor.submit(processador_de_estoque)

# Aguardar que todas as threads (clientes) finalizarem
for t in clientes:
    t.join()

# Mostra os pedidos processados
print(f"{Fore.MAGENTA}{Style.BRIGHT}Pedidos Processados:")
while not fila_de_processados.empty():
    pedido_processado_json = fila_de_processados.get()
    print(f"{Fore.MAGENTA}{Style.BRIGHT} {pedido_processado_json}")

# Mostra o estoque final
print(f"{Fore.CYAN}{Style.BRIGHT}Estoque Final:")
for produto, quantidade in estoque.items():
    print(f"{Fore.CYAN}{Style.BRIGHT} Produto: {produto} | {quantidade} unidades restantes")

print(f"{Fore.CYAN}End")
