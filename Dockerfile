#FROM python:3.6
#
#RUN mkdir -p /usr/src/app
#
#WORKDIR /usr/src/app
#
#COPY . /usr/src/app
#
#RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple
#
#EXPOSE 5000
#
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
#
#CMD ["/bin/bash","/usr/src/app/docker_entry.sh"]
#CMD ["uwsgi" , "--ini" , "/usr/src/app/scm_uwsgi.ini"]


FROM reg.douwa.io/hsbs/python:3.6-dw

COPY . /app

# RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple
RUN pip3 install -r requirements.txt

EXPOSE 5000
CMD ["/bin/bash","docker_entry.sh"]
