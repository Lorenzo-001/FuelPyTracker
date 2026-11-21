# =============================================================================
# FuelPyTracker V2 — Frontend Production Dockerfile (Vite Build + Nginx)
# =============================================================================

# --- Stage 1: Build dell'applicazione React SPA ---
FROM node:22-alpine AS builder

WORKDIR /app

# Copia i file di dipendenze per sfruttare la cache dei layer Docker
COPY package*.json ./
RUN npm ci

# Copia il codice sorgente
COPY . .

# Variabili di build opzionali (default vuoto: usa /api con reverse proxy Nginx)
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

# Compila il bundle di produzione con Vite
RUN npm run build

# --- Stage 2: Runtime Web Server Nginx leggero ---
FROM nginx:1.27-alpine

# Rimuovi la configurazione predefinita di Nginx
RUN rm -rf /etc/nginx/conf.d/*

# Copia la configurazione personalizzata per SPA e reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia gli asset compilati dallo stage di build
COPY --from=builder /app/dist /usr/share/nginx/html

# Esposizione porta standard HTTP
EXPOSE 80

# Healthcheck nativo su Nginx
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget --spider -q http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
