FROM postgres:13

# Устанавливаем переменные окружения для PostgreSQL
ENV POSTGRES_DB=${DB_DATABASE:-pt_bot}
ENV POSTGRES_USER=${DB_REPL_USER:-repl_user}
ENV POSTGRES_PASSWORD=${DB_REPL_PASSWORD:-kali}
ENV MASTER_HOST=${DB_HOST:-db_image}
ENV MASTER_PORT=${DB_PORT:-5432}
ENV REPL_HOST=${DB_REPL_HOST:-DB_REPL_IMAGE}
ENV REPL_PORT=${DB_REPL_PORT:-5432}

RUN mkdir -p /etc/postgresql/ && chmod 750 /var/lib/postgresql/data

ENTRYPOINT ["bash", "-c", "\
cat <<EOF > /etc/postgresql/postgresql.conf \n\
listen_addresses = '*' \n\
port = ${REPL_PORT} \n\
EOF\n\
rm -rf /var/lib/postgresql/data/* \n\
sleep 10 \n\
echo ${POSTGRES_PASSWORD} | pg_basebackup -v -R \\\n\
  -h ${MASTER_HOST} -p ${MASTER_PORT} -U ${POSTGRES_USER} -W -P \\\n\
  -D /var/lib/postgresql/data \n\
echo \"primary_conninfo = 'host=${MASTER_HOST} port=${MASTER_PORT} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}'\" >> /var/lib/postgresql/data/postgresql.auto.conf \n\
docker-entrypoint.sh $@"]

EXPOSE 5432

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]