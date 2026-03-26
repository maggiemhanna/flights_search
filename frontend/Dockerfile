FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build the app
COPY . .
RUN npm run build

# Stage 2: Serve the application
FROM node:18-alpine

WORKDIR /app

# Install serve to run the application
RUN npm install -g serve

# Copy the build output from the previous stage
COPY --from=build /app/dist ./dist

# Cloud Run automatically sets the PORT environment variable (default 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "serve -s dist -l tcp://0.0.0.0:$PORT"]
