FROM ubuntu:20.04

COPY . .

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 \
    python3-pip \
    epiphany-browser \
    webkit2gtk-driver \
    xvfb \
    --no-install-recommends \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r requirements.txt

RUN Xvfb :19 -screen 0 800x600x8 &
ENV DISPLAY=":19"

EXPOSE 5000

CMD python3 run.py
