FROM node:24-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY src ./src
COPY public ./public
COPY private ./private
RUN mkdir -p /app/data
EXPOSE 3000
CMD ["node", "src/server.js"]
