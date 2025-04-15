FROM python
WORKDIR /whiteboard_app
COPY . .
RUN pip install -r requirements.txt
RUN mkdir -p key
EXPOSE 5000
ENTRYPOINT ["python","-u"]
CMD ["app.py"]
