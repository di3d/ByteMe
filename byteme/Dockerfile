# Use an official Node.js image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Expose the dev port (default is 3000)
EXPOSE 3000

# Start the Next.js dev server
CMD ["npm", "run", "dev"]
