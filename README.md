# ByteMe Application 🚀

ByteMe is a microservices-based application designed to handle various functionalities such as customer management, order processing, recommendations, and payment handling using Stripe. Built using Flask, Next.js, Firebase, RabbitMQ, and Docker, it follows modern development practices to ensure scalability, modularity, and secure operations.

## 🛠 Tech Stack

- **Frontend:** Next.js
- **Backend:** Flask migrate, postgres
- **Authentication:** Firebase (used exclusively for user authentication)
- **Payment Integration:** Stripe microservice
- **Messaging:** RabbitMQ for asynchronous communication
- **Containerization:** Docker

## 📜 Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and coding standards
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines, branching strategy, and PR guide
- **[CHANGELOG.md](CHANGELOG.md)** - Automatically generated changelog

## 📥 Installation & Setup

### 1. Prerequisites

1. Install [Node.js](https://nodejs.org/) (v16 or higher).
2. Install [Python](https://www.python.org/) (v3.8 or higher).
3. Install [Docker](https://www.docker.com/) (optional, for containerized deployment).
4. Set up Firebase and Stripe accounts.

1. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```

2. Start the services using Docker Compose:
   ```sh
   docker-compose up -d --build
   ```
