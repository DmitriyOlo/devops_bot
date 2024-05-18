FROM postgres:13

RUN apt-get update && apt-get install -y openssh-server && mkdir /var/run/sshd

ENV POSTGRES_DB=${DB_DATABASE:-pt_bot}
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV REPL_USER=${DB_REPL_USER}
ENV REPL_PASSWORD=${DB_REPL_PASSWORD}
ENV DB_USER=${DB_USER:-root}
ENV DB_PASSWORD=${DB_PASSWORD:-kali}

COPY init.sql /docker-entrypoint-initdb.d/

RUN echo "logging_collector = on" >> /usr/share/postgresql/13/postgresql.conf.sample && \
    echo "log_directory = '/var/log/postgresql'" >> /usr/share/postgresql/13/postgresql.conf.sample && \
    echo "log_filename = 'postgresql-13-main.log'" >> /usr/share/postgresql/13/postgresql.conf.sample

RUN echo "${DB_USER}:${DB_PASSWORD}" | chpasswd

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN echo "host replication repl_user 0.0.0.0/0 md5" >> /usr/share/postgresql/13/pg_hba.conf.sample
RUN echo "wal_level=replica" >> /usr/share/postgresql/13/postgresql.conf.sample
RUN echo "hot_standby=on" >> /usr/share/postgresql/13/postgresql.conf.sample
RUN echo "max_wal_senders=10" >> /usr/share/postgresql/13/postgresql.conf.sample
RUN echo "max_replication_slots=10" >> /usr/share/postgresql/13/postgresql.conf.sample
RUN echo "hot_standby_feedback=on" >> /usr/share/postgresql/13/postgresql.conf.sample
RUN echo "log_replication_commands=on" >> /usr/share/postgresql/13/postgresql.conf.sample

EXPOSE 22
EXPOSE 5432

CMD service ssh start && docker-entrypoint.sh postgres