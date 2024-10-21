# Projeto para a disciplina de Programação Paralela e Multicore.

## Descrição:
Desenvolver uma aplicação paralela para gerenciar a compra de produtos durante grandes promoções, como a Black
Friday, onde milhões de usuários acessam a plataforma simultaneamente para aproveitar descontos. A aplicação deve ser
capaz de processar um grande volume de transações em tempo real, gerenciar estoques de forma eficiente, e evitar problemas
como overselling ou crashes do sistema devido à alta demanda. Os alunos implementarão técnicas de programação paralela
para balancear a carga entre os servidores, reduzir tempos de resposta, e assegurar que as transações sejam processadas de
forma correta e rápida.

## Funcionalidades:

- **Simulação de Clientes**: Vários clientes geram pedidos aleatórios para diferentes produtos.
- **Processamento Concorrente**: O sistema processa pedidos usando múltiplas threads para garantir que a atualização do estoque ocorra de forma segura e eficiente.
- **Métricas de Desempenho**: Coleta de métricas sobre pedidos processados e pedidos inválidos (por falta de estoque) usando a biblioteca Prometheus + Grafana para visualização em dashboards.
- **Atualização do Estoque**: O estoque é atualizado em tempo real, e as informações são impressas no console.

## Tecnologias Utilizadas:

- Python
- `threading` para concorrência
- `queue` para gerenciar pedidos
- `random` para gerar pedidos aleatórios
- `json` para formatação de dados
- `colorama` para colorir a saída do console
- `prometheus_client` para monitoramento de métricas

## Dependências:
- Certifique-se de ter as dependências instaladas:
  ```bash
  pip install colorama prometheus_client

- Para mais informações, seguir info.txt
