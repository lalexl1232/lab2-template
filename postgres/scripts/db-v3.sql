CREATE DATABASE cars;
GRANT ALL PRIVILEGES ON DATABASE cars TO program;

CREATE DATABASE rentals;
GRANT ALL PRIVILEGES ON DATABASE rentals TO program;

CREATE DATABASE payments;
GRANT ALL PRIVILEGES ON DATABASE payments TO program;

\ir /docker-entrypoint-initdb.d/scripts/init-cars-db.sql
\ir /docker-entrypoint-initdb.d/scripts/init-rental-db.sql
\ir /docker-entrypoint-initdb.d/scripts/init-payment-db.sql