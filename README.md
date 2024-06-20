## Introduction

This application accepts financial transaction data and categorises the transactions appropriately. These transactions can then be queried directly by connecting to the database or by using one of the custom query endpoints.

---
## Steps to run the application

Follow the steps below to run the application. These steps are written under the assumption that docker is already installed and running, and that the developer has a basic knowledge of github.

### 1. Clone the Repository 

Clone the repository from https://github.com/lauren-mulholland/citro-assessment.git

### 2. Set the Environment Variables in Docker-Compose

Set the environment variables in `.env` file, in the root folder, as they are referenced within `docker-compose.yaml`. The database related environment variables have already been set in the `.env` file (since this is not a production application with real data). Set a valid key for the `OPENAI_API_KEY`.

### 3. Building and Running Docker Compose

Build and run the services defined in `docker-compose.yaml` by running the following command:

```bash
docker-compose up -d --build
```
---
## Using the application
Move onto this section assuming the application was successfully setup and the docker containers are running.

### The API documentation
The API is served at http://0.0.0.0:8000 and it is documented and can be tested at http://0.0.0.0:8000/docs. On this page, you can click into each endpoint to view a description, the accepted parameters and the format of the request and response bodies. There are 5 endpoints available which can be used to load and query transactional data. These endpoints are not secured at this point. 

#### Endpoints for Loading Data
Use the following endpoints to load data either as a single transaction or as a list of transactions. The format of the payloads is documented at the link above.
- **POST** /transaction
- **POST** /transaction_list

#### Endpoints for Querying Data
Use the following endpoints to query data. As documented in the link above, use the query parameters to filter the data by category, timestamp_to and timestamp_from as applicable.
- **GET** /transaction_category_statistics
- **GET** /get_transactions_by_category
- **GET** /counterparts_by_category

### Connecting to the Database
The easiest way to connect to the clickhouse database is by using the HTTP interface and WebUI. In a browser, navigate to http://localhost:8123/play, enter the username `default` and password `default` to run any custom query. For further instructions on how to use the HTTP interface, see instructions at https://clickhouse.com/docs/en/interfaces/http.

NB. Clickhouse is constantly merging `parts` in the background. To explicitely ensure the expected result is returned, use the `FINAL` keyword to ensure all parts have been merged. For example:

```SQL 
SELECT * FROM citro_analytics.transactions FINAL
```
There are other ways to connect to the database e.g. the Clickhouse CLI or a SQL Client with the Clickhouse driver. Use the following details (equiv to those in the .env file) to connect:

- `host`:`localhost`
- `port`: `8123`
- `username`: `default`
- `password`: `default`
- `database`: `citro_analytics`

---
## Explanation of Approach

- **API**: I've chosen to use FastAPI to build the endpoints for the application. It is lightweight and allows us to easily document the API. I have not documented the API explicitely in this readme as the descriptions, models and examples can be found by navigating to the docs page.
- **Database**: I've chosen to use a Clickhouse database for this task. Clickhouse is very fast and is designed for handling large volumes of data (presumably such as financial transaction data). When the clickhouse container is built, the transactions table will be created based on the initialisation script `docker-entrypoint-initdb.d/init.sql`. The script will create a table called "citro_analytics"."transactions" with the ReplacingMergeTree engine. The ReplacingMergeTree will create or replace records in the table based on the primary key transactionId, which is how the POST method endpoints are idempotent.

