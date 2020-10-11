FROM node:lts-alpine3.11 as build-stage
WORKDIR /opt/client
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM alpine:latest
COPY --from=build-stage /opt/client/dist /opt/client
