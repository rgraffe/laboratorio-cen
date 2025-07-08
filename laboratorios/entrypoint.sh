#!/bin/sh
set -e

echo "Esperando a la base de datos..."
until nc -z db 5432; do
  sleep 1
done

echo "Ejecutando migraciones de Drizzle..."
./node_modules/.bin/drizzle-kit push

echo "Iniciando la aplicación..."
npm run dev