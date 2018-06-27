# LuziaRules
Proyecto Luzia Easy Rules

**Requisitos para la instalación**

 - Apache2


**Guia de instalación ubuntu/debian**.

- instalar apache

    $ sudo apt-get install apache2

- Copiar las carpetas "app" y "lib" en /var/www/html

    $ cp app/ /var/www/html
    
    $ cp lib/ /var/www/html

- Ya esta la demo funcionando en 127.0.0.1/app




**Guia de instalación Centos/fedora/rhel**

- instalar apache *(ejecutar con root)*

    $ yum -y install httpd

- chequear que apache inicie con el sistema operativo

    $ chkconfig --levels 235 httpd on

- Iniciar apache

    $ /etc/init.d/httpd start

- Copiar las carpetas "app" y "lib" en /var/www/html

    $ cp app/ /var/www/html
    
    $ cp lib/ /var/www/html

- Ya esta la demo funcionando en 127.0.0.1/app




***NOTA: Los datos de ejemplo se cargarán a medida que va visitando las distintas secciones del sitio con mensajes alertándolo al respecto.***
