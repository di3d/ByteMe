# ## Layer caching for faster builds
# # Use an official Node.js image
# FROM node:18

# # Set working directory
# WORKDIR /app

# # Copy package.json and package-lock.json first
# COPY package*.json ./

# # Install dependencies
# RUN npm install

# # Copy the rest of the app
# COPY . .

# # Expose the dev port (default is 3000)
# EXPOSE 3000

# # Start the Next.js dev server
# CMD ["npm", "run", "dev"]

##Unoptimised build
# # Use an official Node.js image
# FROM node:18

# # Set working directory
# WORKDIR /app

# # Copy the rest of the app
# COPY . .

# # Install dependencies
# RUN npm install

# # Expose the dev port (default is 3000)
# EXPOSE 3000

# # Start the Next.js dev server
# CMD ["npm", "run", "dev"]


#Copy files that change rarely (dependencies) before files that change frequently (source code)

# Use Alpine version for smaller base image (~120MB vs ~900MB)
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies with cache optimizations
RUN npm install && npm cache clean --force

# Copy the rest of the app
COPY . .

# Expose the dev port (default is 3000)
EXPOSE 3000

# Start the Next.js dev server
CMD ["npm", "run", "dev"]
