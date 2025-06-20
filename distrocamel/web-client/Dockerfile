# Use Node.js LTS
FROM node:18-alpine

WORKDIR /app

# Install app dependencies
COPY web-client/package*.json ./
RUN npm install

# Copy app source code
COPY web-client/ .

# Build the app
RUN npm run build

# Expose the app port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
