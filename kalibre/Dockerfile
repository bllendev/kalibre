# Stage 1: Build the React app
FROM node:16 AS frontend
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

# Stage 2: Serve the built app with a lightweight web server
FROM node:16 AS production
ENV NODE_ENV=production
WORKDIR /app
COPY --from=frontend /app/dist ./frontend
RUN yarn global add serve
EXPOSE 3000
CMD ["serve", "-s", "frontend"]
