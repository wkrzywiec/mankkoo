FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04

ENV PYTHON_VERSION=3.10
ENV UV_VERSION=0.11.21

ENV NVM_DIR=/usr/local/nvm
ENV NODE_VERSION=20.18.0
# replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Python
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python${PYTHON_VERSION} \ 
    && ln -s /usr/bin/python3 /usr/bin/python \
    && apt-get install -y python3-pip

# uv
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh \
    && uv --version

# nvm
RUN apt-get update \
    && apt-get install build-essential libssl-dev

RUN mkdir -p $NVM_DIR \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Nodejs, npm
# install node and npm
RUN source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH=$NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# confirm installation
RUN node -v
RUN npm -v
RUN npm install -g pnpm


# install Taskfile
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
# RUN chmod +x /usr/local/bin/task.bash && source /usr/local/bin/task.bash
RUN task --version
