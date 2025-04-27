FROM python:3.9-slim
WORKDIR /whiteboard_app
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install -y libssl-dev libffi-dev && \
    apt-get clean
RUN mkdir -p key
EXPOSE 5000
ENTRYPOINT ["python","-u"]
CMD ["app.py"]
