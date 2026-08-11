FROM node:20-slim

# Install dependencies for better-sqlite3
RUN apt-get update && apt-get install -y python3 make g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /data

# Set environment
ENV NODE_ENV=production
ENV DATABASE_URL=file:/data/custom.db
ENV PORT=3000

# Expose port
EXPOSE 3000

# Build Next.js
RUN npm run build

# Start the app
CMD ["npm", "start"]
