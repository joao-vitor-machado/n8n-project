CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    client_key VARCHAR(36) NOT NULL,
    document_number VARCHAR(18) NOT NULL,
    name VARCHAR(255) NOT NULL,
    UNIQUE (client_key),
    UNIQUE (document_number)
);

CREATE TABLE contract (
    id SERIAL PRIMARY KEY,
    contract_key VARCHAR(36) NOT NULL,
    client_id INT NOT NULL REFERENCES client(id),
    start_date DATE NOT NULL,
    active BOOLEAN NOT NULL,
    UNIQUE (contract_key)
);

CREATE TABLE consumption_reading (
    id SERIAL PRIMARY KEY,  
    reading_key VARCHAR(36) NOT NULL,
    contract_id INT NOT NULL REFERENCES contract(id),
    reading_date DATE NOT NULL,
    reading_value DECIMAL(10, 2) NOT NULL,
    UNIQUE (reading_key)
);