FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN rm -f package-lock.json
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
