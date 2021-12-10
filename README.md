## Universidade Estadual de Campinas - Instituto da Computação

## Disciplina: MC855-2s2021

### Professor e Assistente

| Nome                     | Email                   |
| ------------------------ | ------------------------|
| Professora Juliana Borin | jufborin@unicamp.br     |
| Assistente Paulo Kussler | paulo.kussler@gmail.com |


### Equipe

| Nome                         | RA               | Email                  | ID Git                |
| ---------------------------- | ---------------- | ---------------------- |---------------------- |
| Adivair Santana Ramos        | 193325           | a193325@dac.unicamp.br | A193325               |
| Fabio Stori                  | 196631           | f196631@dac.unicamp.br | fabioStori            |
| Felipe Duarte Domingues      | 171036           | f171036@dac.unicamp.br | exofelipe             |
| Gabriel Francioli Alves      | 172111           | g172111@dac.unicamp.br | gfrancioli            |

# Descrição do projeto:
Este projeto descreve a estrutura da API e banco de dados utilizada para o funcionamento da plataforma Invent-io

### Estrutura:
As rotas da API estão descritas no arquivo routes/api_v1.py
As classes relacionadas com a comunicação com o banco de dados MongoDB estão disponíveis no diretório database, sendo que o arquivo database/classes.py contém as 
classes responsáveis por cada collection do banco.

O arquivo options.conf pode ser utilizado para configurar a aplicação. É recomendado alterar os parâmetros _api.secret_key_, _api.debug_ e _mongodb.password_ para aplicações em produção.

O arquivo docker-compose.yml pode ser alterado para modificar o comportamento da aplicação. Ao alterar a senha do banco em _options.conf_ ou a porta de execução, é necessário alterar também a arquitetura docker.

### Tecnologias:
Nesse projeto utilizamos [Flask](https://flask.palletsprojects.com/en/2.0.x/) com interação com um banco No-SQL([MongoDB](https://www.mongodb.com/)) e uma estrutura de containers com [Docker](https://www.docker.com/) para facilitar o deploy da aplicação.

### Ambientes: 
O ambiente de produção está hospedado em uma máquina virtual da nuvem do IC, rodando com um container Docker. 
Ambientes de desenvolvimento podem ser facilmente criados com a instalação do cliente docker.

# Instalação:
Para executar a aplicação é necessário que o [Docker](https://www.docker.com/) esteja instalado.
Na raiz do projeto, execute o comando para que os containers sejam instanciados
```sh
docker-compose up --build
```

# Acessando aplicação local:
Após executar esse comando o container será criado e a aplicação estará disponível para requisições em localhost:<porta-selecionada>, inclusive com um MongoDB local.
As requisições podem ser feitas via [Postman](https://www.postman.com/) ou qualquer outro API Client.

### Acessando o ambiente de produção:
A aplicação está hospedada no servidor cloud da Unicamp, com o seguinte endereço: https://invent-io.ic.unicamp.br/.

### Professora Juliana no Gitlab:
O projeto pode ser encontrado por completo, inclusive com as credenciais do IC no [Gitlab](link) da Profa. Juliana.
