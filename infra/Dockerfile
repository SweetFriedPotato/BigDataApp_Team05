FROM php:8.2-apache
RUN docker-php-ext-install pdo_mysql
RUN printf 'ServerName localhost\n' > /etc/apache2/conf-available/server-name.conf && a2enconf server-name
COPY infra/php.ini /usr/local/etc/php/conf.d/seasonal.ini
WORKDIR /var/www/html
