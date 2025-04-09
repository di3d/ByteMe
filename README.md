# ByteMe Application 🚀

ByteMe is a microservices-based application designed to handle various functionalities such as customer management, order processing, recommendations, and payment handling using Stripe. Built using Flask, Next.js, Firebase, RabbitMQ, and Docker, it follows modern development practices to ensure scalability, modularity, and secure operations.

## 🛠 Tech Stack

- **Frontend:** Next.js
- **Backend:** postgres
- **Authentication:** Firebase (used exclusively for user authentication)
- **Payment Integration:** Stripe service
- **Email Notification:** SendGrid service
- **Messaging:** RabbitMQ for asynchronous communication
- **Containerization:** Docker


## 📥 Installation & Setup

### 1. Prerequisites

1. Install [Node.js](https://nodejs.org/) (v16 or higher).
2. Install [Python](https://www.python.org/) (v3.8 or higher).
3. Install [Docker](https://www.docker.com/) (optional, for containerized deployment).
4. Set up Firebase, Stripe and SendGrid credentials. 
   a. Firebase credentials go into .env file at root of directory
   b. Stripe credentials go to root of /stripe folder, add default URLs and rabbitMQ details:
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

   
