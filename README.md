### Introduction

This application accepts financial transaction data and categorises the transactions appropriately. These transactions can then be queried directly by connecting to the database or by using one of the custom query endpoints.

---

### Steps to Run the Application

Follow the steps below to run the application. These steps are written under the assumption that Docker is already installed and running, and that the developer has a basic knowledge of GitHub.

#### 1. Clone the Repository 

Clone the repository from https://github.com/lauren-mulholland/citro-assessment.git

#### 2. Set the Environment Variables in Docker-Compose

Set the environment variables in the `.env` file in the root folder, as they are referenced within `docker-compose.yaml`. The database-related environment variables have already been set in the `.env` file (since this is not a production application with real data). Set a valid key for the `OPENAI_API_KEY`.

#### 3. Building and Running Docker Compose

Build and run the services defined in `docker-compose.yaml` by running the following command:

```bash
docker-compose up -d --build
```

---

### Using the Application

Move on to this section assuming the application was successfully set up and the Docker containers are running.

#### The API Documentation

The REST API is served at http://0.0.0.0:8000 and is documented and testable at http://0.0.0.0:8000/docs. On this page, you can navigate to each endpoint to display details such as the description, format, and example payloads. There are 5 endpoints available that can be used to load and query transactional data. These endpoints are not secured at this point.

##### Endpoints for Loading Data

Use the following endpoints to load data either as a single transaction or as a list of transactions. The format of the request body is documented at the link above.

- **POST** /transaction
- **POST** /transaction_list

##### Endpoints for Querying Data

Use the following endpoints to query data. As documented in the link above, use the query parameters to filter the data by category, timestamp_to, and timestamp_from as applicable.

- **GET** /transaction_category_statistics
- **GET** /get_transactions_by_category
- **GET** /counterparts_by_category

#### Connecting to the Database

The easiest way to connect to the ClickHouse database is by using the HTTP interface and WebUI. In a browser, navigate to http://localhost:8123/play, enter the username `default`, and password `default` to run any custom query. For further instructions on how to use the HTTP interface, see the instructions at https://clickhouse.com/docs/en/interfaces/http.

Note: ClickHouse is constantly merging `parts` in the background. To explicitly ensure the expected result is returned, use the `FINAL` keyword to ensure all parts have been merged. For example:

```sql
SELECT * FROM citro_analytics.transactions FINAL
```

There are other ways to connect to the database, e.g., the ClickHouse CLI or a SQL client with the ClickHouse driver. Use the following details (equivalent to those in the .env file) to connect:

- `host`: `localhost`
- `port`: `8123`
- `username`: `default`
- `password`: `default`
- `database`: `citro_analytics`

---

### Explanation of Approach

- **API**: I've chosen to use FastAPI to build the endpoints for the application. It is lightweight and allows us to easily document the API. I have not explicitly documented the API in this README as the descriptions, models, and examples can be found by navigating to the docs page.

- **Database**: I've chosen to use a ClickHouse database for this task. ClickHouse is very fast and is designed for handling large volumes of data, such as financial transaction data. When the ClickHouse container is built, the `transactions` table will be created based on the initialization script `docker-entrypoint-initdb.d/init.sql`. The script will create a table called `"citro_analytics"."transactions"` with the ReplacingMergeTree engine. The ReplacingMergeTree will create or replace records in the table based on the primary key `transactionId`, which is how the POST method endpoints are idempotent.

---