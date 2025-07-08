FROM node:20

WORKDIR /app

COPY package*.json ./
ENV NODE_ENV=development
RUN npm install

# Instala netcat para wait-for-db
RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

COPY .env .env

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 3001

CMD ["/app/entrypoint.sh"]