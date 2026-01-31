# Stage 1: Build the React app
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all frontend code
COPY . .

# Build the React app for production
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built files from stage 1
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config (we'll create this next)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
