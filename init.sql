CREATE DATABASE IF NOT EXISTS promo_app;

USE promo_app;

CREATE TABLE IF NOT EXISTS estoque (
    produto VARCHAR(50) PRIMARY KEY,
    quantidade INT
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto VARCHAR(50),
    quantidade INT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS erros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto VARCHAR(50),
    mensagem VARCHAR(255),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados iniciais no estoque
INSERT INTO estoque (produto, quantidade) VALUES
('produtoA', 100),
('produtoB', 50),
('produtoC', 200),
('produtoD', 30),
('produtoE', 100);
