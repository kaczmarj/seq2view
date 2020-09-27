FROM node:lts-alpine3.11 as build-stage
WORKDIR /opt/client
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.18.0-alpine as production-stage
COPY --from=build-stage /opt/client/dist /opt/client
COPY nginx.conf /etc/nginx/nginx.conf
