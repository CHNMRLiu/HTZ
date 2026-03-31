FROM node:22-slim

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

EXPOSE 5670

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5670"]
