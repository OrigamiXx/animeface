FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-devel

ENV DEBIAN_FRONTEND=noniteractive
RUN apt update -y && \
    apt install -y \
    libopencv-dev

ARG UID
RUN useradd -l -m -u ${UID} dockeruser
USER ${UID}

COPY docker/torch/requirements.txt requirements.txt
RUN pip --default-timeout=100 install -r requirements.txt
