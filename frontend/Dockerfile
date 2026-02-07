# frontend/Dockerfile

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app

# Copy built files
COPY --from=builder /app/dist ./dist

COPY --from=builder /app/vite.config.js ./vite.config.js

# Copy package files
COPY --from=builder /app/package*.json ./
RUN npm install --production=false

EXPOSE 4173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]