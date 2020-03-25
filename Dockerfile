FROM python:3-alpine

RUN apk add --no-cache nginx openssh-client && pip3 install flask
COPY . /root/
COPY default.conf /etc/nginx/conf.d/
COPY www /var/www/html/

CMD ["/bin/ash", "/root/start.sh"]
