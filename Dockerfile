FROM amazonlinux

RUN yum update -y
RUN yum install -y \
    gcc \
    openssl-devel \
    libpq-dev \
    python-dev \
    zlib-devel \
    libffi-devel \
    python3 \
    python3-pip \
    git \
    wget && \
    yum -y clean all
RUN yum -y groupinstall development
WORKDIR /opt

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY youtube_scraper youtube_scraper
WORKDIR /opt/youtube_scraper
ENTRYPOINT ["/usr/bin/python3", "/opt/youtube_scraper/run.py"]
