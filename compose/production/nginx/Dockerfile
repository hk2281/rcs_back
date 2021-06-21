FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./certs /etc/nginx/certs
COPY nginx.conf /etc/nginx/conf.d