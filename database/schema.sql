create database todo_app;
use todo_app;

create table tarefas (
id INT PRIMARY KEY AUTO_INCREMENT,
titulo VARCHAR(255) NOT NULL, 
descricao TEXT,
completo BOOLEAN DEFAULT FALSE,
prioridade ENUM('baixa','media','alta') DEFAULT 'media',
criado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
atualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_completo(completo),
INDEX idx_criado(criado),
INDEX idx_titulo(titulo)
);

create table categorias (
id INT PRIMARY KEY AUTO_INCREMENT,
nome VARCHAR(50) NOT NULL UNIQUE,
cor VARCHAR(7) DEFAULT '#6a89cc',
criado TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
