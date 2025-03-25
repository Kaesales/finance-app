# Subir o ambiente com docker-compose
up:
    docker-compose -p finance_api up -d --build

# Parar e remover o ambiente com docker-compose
down:
    docker-compose -p finance_api down

# Visualizar logs dos contêineres
logs:
    docker-compose -p finance_api logs -f

# Reconstruir e subir o ambiente
rebuild:
    docker-compose -p finance_api up -d --build

# Limpar tudo (contêineres, redes e volumes)
clean:
    docker-compose -p finance_api down -v --rmi all

# Executar comandos no contêiner da API
exec-api:
    docker exec -it finance_api-api-1 /bin/bash

# Executar comandos no contêiner do banco de dados
exec-db:
    docker exec -it finance_api-db-1 /bin/bash

# Listar contêineres do projeto
ps:
    docker-compose -p finance_api ps