FROM python:3.6
RUN mkdir -p /var/www/blog
WORKDIR /var/www/blog
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /var/www/blog
RUN pip install -r /var/www/blog/requirements.txt
RUN rm -rf /var/www/blog
COPY . /var/www/blog
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:5050"]