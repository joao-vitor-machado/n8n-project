## PROJETO N8N - 39A

### GUIA PARA RODAR O AMBIENTE
- com o docker devidamente instalado, utilizar o comando ```docker compose up --build```
- entrar em ```http://127.0.0.1:5678```, onde o n8n estar'a hospedado;
- uma vez criado o usuario e senha no n8n, importar o workflow ```n8n_workflow.json``` disponível na pasta de assets do projeto;
- o modelo proposto para o input de dados está na pasta data, também em assets. O script ```zip_unzip.py``` pode ser utilizado para criar o arquivo output.zip que pode ser enviado no workflow que popula o baco de dados;
- Também é necessário adicionar as credenciais (api key fornecida) do gemini no nó de ```Message a model```;

### GUIA DE USO
Foram criados 3 workflows:
    - O primeiro que popula o banco de dados iterando sobre o resultado dos csv descompactados do envio de arquivo que populam o banco através de POSTs na API;
    - O segundo é um fluxo simples que preenche o requisito de consulta da API;
    - O terceiro envolve uma requisição GET para a API e utilização desses dados para a criação de um arquivo .pdf que resume o consumo dos clientes e os outliers;

### OPORTUNIDADES DE MELHORIA
- Adicionar uma camada de middleware para o gerenciamento de sessões do banco de dados;
- Adicionar uma camada de dados para centralizar a consulta e criação de recursos;
- Adicionar um template HTML padrão para a IA se basear. Hoje ela cria o HTML por conta própria ao invés de apenas preencher um HTML com os dados extraídos. Isso faz com que a cada iteração um novo modelo de HTML seja gerado.