FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN rm -rf node_modules package-lock.json
RUN npm install

ARG VITE_API_BASE_URL
ARG VITE_WS_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_URL=$VITE_WS_URL

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
