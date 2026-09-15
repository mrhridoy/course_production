# ── Stage 1: install deps ─────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ── Stage 2: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# NEXT_PUBLIC_API_URL: public domain baked into client-side JS.
ARG NEXT_PUBLIC_API_URL=https://student.ictbangladesh.bd
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# API_INTERNAL_URL: Docker-internal hostname for Next.js rewrites + SSR fetches.
ARG API_INTERNAL_URL=http://localhost:8000
ENV API_INTERNAL_URL=$API_INTERNAL_URL

COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Ensure public/ exists so the COPY in the runner stage never fails
RUN mkdir -p /app/public
RUN npm run build

# ── Stage 3: minimal runtime image ───────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Next.js standalone output copies only what's needed — no node_modules bloat.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Copy public/ folder (guaranteed to exist — created in builder stage above)
COPY --from=builder /app/public ./public

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
