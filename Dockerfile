FROM python:3

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ADD requirements.txt ./
ADD ec2_price_fetcher.py ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "python ec2_price_fetcher.py --s3_region ${S3_REGION} ${BUCKET_NAME}"]
