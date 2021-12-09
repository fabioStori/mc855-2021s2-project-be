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
Esta parte do projeto é focada em fazer a interação com os sensores, banco de dados e a estrutura do deploy a partir do Docker. 

### Estrutura:
O projeto possui uma classe do banco de dados, onde são definidas todas as collections e são feitas todas as interações (CRUD) da aplicação.
Os endpoints estão todos presentes no mesmo arquivo com o código bem simples, já que as interações são feitas na classe do banco.
A arquivo do docker-compose está presente na raiz do projeto e possui todas as configurações do container que é executado na máquina virtual que disponibiliza a aplicação. 

### Tecnologias:
Nesse projeto utilizamos [Flask](https://flask.palletsprojects.com/en/2.0.x/) com interação com um banco No-SQL([MongoDB](https://www.mongodb.com/)) e uma estrutura de containers com [Docker](https://www.docker.com/).

### Ambientes: 
O ambiente de produção está hospedado em uma máquina virtual da nuvem do IC, rodando com um container Docker. 
O projeto não possui nenhum ambiente de dev, o desenvolvimento está sendo feito e testado localmente e, depois das novas funcionalidades terem sido testadas, é feito o deploy para o ambiente de produção.

# Instalação:
O projeto precisa do [Python3.8](https://www.python.org/downloads/release/python-380/), [Pip](https://pip.pypa.io/en/stable/installation/) e o [Docker](https://www.docker.com/) instalados para a execução.
Na raiz do projeto, execute o comando para a instalação das bibliotecas.
```sh
pip install -r ./requirements.txt
```

# Acessando aplicação local
Após instalar as dependências, execute o comando para subir o container.
```sh
docker-compose up --build
```
Após executar esse comando o container será criado e a aplicação estará disponível para requisições em localhost:<porta-selecionada>, inclusive com um MongoDB local.

### Acessando o ambiente de produção:
A aplicação está hospedada no servidor cloud da Unicamp, com o seguinte endereço: https://invent-io.ic.unicamp.br/.

### Professora Juliana no Gitlab:
O projeto pode ser encontrado por completo, inclusive com as credenciais do IC no [Gitlab](link) da Profa. Juliana.
