# Development Dockerfile for Next.js Frontend

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Create next user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3677

# Set environment variable
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3677/api/health || exit 1

# Start the application in development mode
CMD ["npm", "run", "dev"]