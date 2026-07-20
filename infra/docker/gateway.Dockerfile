# ---- Stage 1: builder ----
FROM node:20-slim AS builder
WORKDIR /app
COPY apps/gateway/package*.json ./
RUN npm ci
COPY apps/gateway .
RUN npm run build

# ---- Stage 2: runner ----
FROM node:20-slim
WORKDIR /app
COPY apps/gateway/package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/main.js"]