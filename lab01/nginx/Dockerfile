FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*
COPY html/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /usr/share/nginx/html/assets/manualfile
RUN echo "FLAG{b2r_nginx_401_bypass_d6f8}\n\nCongrats! You bypassed the 401 restriction.\n\nLook for clues about internal services..." > /usr/share/nginx/html/assets/manualfile/Bot2rootsensitivefile.txt

EXPOSE 80
