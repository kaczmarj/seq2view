FROM node:lts-alpine3.11 as build-stage
WORKDIR /opt/client
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.18.0-alpine as production-stage
WORKDIR /opt/client
COPY --from=build-stage /opt/client/dist .
COPY nginx.conf /etc/nginx/nginx.conf
