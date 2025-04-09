# ByteMe Application 🚀

ByteMe is a microservices-based application designed to handle various functionalities such as customer management, order processing, recommendations, and payment handling using Stripe. Built using Flask, Next.js, Firebase, RabbitMQ, and Docker, it follows modern development practices to ensure scalability, modularity, and secure operations.

## 🛠 Tech Stack

- **Frontend:** Next.js
- **Backend:** postgres, hosted on postgres.yanservers.com
- **Authentication:** Firebase (used exclusively for user authentication)
- **Payment Integration:** Stripe service
- **Email Notification:** SendGrid service
- **Messaging:** RabbitMQ for asynchronous communication
- **Containerization:** Docker

## 📥 Installation & Setup

### 1. Prerequisites

1. Install [Node.js](https://nodejs.org/) (v16 or higher).
2. Install [Python](https://www.python.org/) (v3.8 or higher).
3. Install Docker:
   - For **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
   - For **macOS/Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
4a. If you're evaluating this file for ESD project, then there will be a .env files google docs in the zipped up folder, under Deliverables/codebase. Inside, there are multiple .env files organized under their relative path from the root of our code repository.
4b. Set up Firebase, Stripe and SendGrid credentials.
   a. Firebase credentials go into root of /byteme folder (our frontend).

   b. Stripe credentials go into .env at root of /stripe folder, add default URLs and rabbitMQ details:

      # Default URLs

      DEFAULT_SUCCESS_URL=http://localhost:3000/success
      DEFAULT_CANCEL_URL=http://localhost:3000/checkout?canceled=true

      # RabbitMQ settings

      RABBITMQ_HOST=localhost
      RABBITMQ_PORT=5672
      RABBITMQ_USER=guest
      RABBITMQ_PASSWORD=guest

   c. SendGrid credentials go to root of /email_service folder, add rabbitMQ details:
      EMAIL_FROM_NAME=ByteMe Store
      RABBITMQ_HOST=rabbitmq
      RABBITMQ_PORT=5672
      RABBITMQ_USER=guest
      RABBITMQ_PASS=guest

### Deployment

1. Change directory into the /byteme folder (case-sensitive):
   cd byteme
2. Run npm install
   npm install
3. Start up the frontend in development mode
   npm run dev
4. In another terminal, make sure you're at the root and run the docker-compose file, wait for ALL services to finish building
   docker compose up -d --build
5. Head to localhost:3000 to access our website and access all our features! Happy building :D
