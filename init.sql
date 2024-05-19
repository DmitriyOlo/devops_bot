--SELECT 'CREATE DATABASE replacedbname'

--WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedbname')\gexec;



--DO $$

--BEGIN

   -- IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replaceREPLUSER') THEN

     --   CREATE USER replaceREPLUSER WITH REPLICATION ENCRYPTED PASSWORD 'replaceREPLPASSWORD';

   -- END IF;

   -- IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replaceDBUSER') THEN

    --    CREATE USER replaceDBUSER WITH ENCRYPTED PASSWORD 'replaceDBPASSWORD';

  --  END IF;

--END $$;



--ALTER USER replaceDBUSER WITH PASSWORD 'replaceDBPASSWORD';

psql
CREATE DATABASE replacedbname;
\c replacedbname;
CREATE TABLE IF NOT EXISTS emails (id SERIAL PRIMARY KEY,email VARCHAR(255) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_numbers (id SERIAL PRIMARY KEY,phone_number VARCHAR(30) NOT NULL);

INSERT INTO phone_numbers (phone_number) VALUES ('88005553535') ON CONFLICT DO NOTHING;
INSERT INTO emails (email) VALUES ('example@test.try') ON CONFLICT DO NOTHING;