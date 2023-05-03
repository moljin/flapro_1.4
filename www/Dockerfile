FROM python:3.9.9

# 캐시를 없애기 위해서 의미없는 RUN 을 한번 해줘야 한다.
RUN echo "testing3"

# github에서 내려받는 작업: 내려받으면 FDKproject0.1폴더가 만들어진다.
WORKDIR /home/moljin/
RUN git clone https://github.com/moljin/FLAPRO_1.3.git

# 만들어진 FDKproject0.1 폴더에서 작업
WORKDIR /home/moljin/FLAPRO_1.3/
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
# flask 폴더 안에 있는 app.py실행
#CMD ["python3", "flask/app.py", "--host=0.0.0.0"]

#""" #### gunicorn에서 app:app를 사용하기 위해서 WORKDIR를 app.py가 위치한 경로로 다시 지정 #### """
WORKDIR /home/moljin/FLAPRO_1.3/
#WORKDIR /home/moljin/FDKproject0.2.1/flask_www/
# nginx와 연동하면서....이거는 죽였다.
#CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "app:app"]


