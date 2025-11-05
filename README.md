# tcc_api_atutenticacao

docker run -d -e SECRET_KEY="_XOC-izydwVUdAg-QNN49NNiZtzD7mRzdUOepNzTtJEtwlikBdiWPT96nJQ8IqPBUh1X6P13GN3hE-sRUa1VIQ" -e ALGORITHM="HS256" -e DB_HOST="host.docker.internal" -e DB_PORT="5432" -e DB_USER="postgres" -e DB_PSW="postgres" -e DB_DATABASE="postgres" -p 8000:8000  leandrorodriguescarneiro/tcc_api_autenticacao:latest
