## Setting Up Your Local Environment

Before running the project, ensure you have Python installed and install dependencies:

1. **Verify Python Installation**

   ```sh
   python --version
   ```

   Ensure Python version **3.9 or earlier** is installed.

   Do this inside VSCode terminal. If the output is an error, check the following:

   - In search bar, search "add or remove programs". Search "python" within "add or remove programs". It should show the version of python you have installed.
   - If there's nothing there, install it at [python.org](https://www.python.org/downloads/). The latest stable version is version 3.13.
   - After installing it, in VSCode,
     - press `ctrl` + `shift` + `p`
     - search "python: create environment"
     - Click on "Venv"
     - Click on the latest version of python you have
     - Tick "requirements.txt" checkbox and press "OK"
     - Your repository should now have a ".venv" file.

2. **Install Required Dependencies**
   Navigate to the project's root directory and install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Running Docker Compose

To initialise and start the database and microservices, run:

```sh
docker-compose up -d --build
```

- `-d` runs the services in the background.
- `--build` rebuilds images before starting containers.

## Flask Migrate

[Flask-Migrate](https://flask-migrate.readthedocs.io/) is used as an ORM for database management.

### Benefits

- Reduces the need for raw SQL queries.
- Simplifies schema management for future cloud deployment.

### First-Time Database Migration

Navigate to the microservice folder first:

```sh
cd ./order  # or ./customer ./make_purchase
```

Run the following commands to create the migration files and apply them:

```sh
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

Migration files should appear inside the `migrations/` folder.

### Example Table Definition

```python
class Customer(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
```
