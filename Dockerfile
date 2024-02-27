ARG BASE_IMAGE=python:3.9-slim
FROM $BASE_IMAGE

LABEL maintainer="Yuchen Jin <cainmagi@gmail.com>" \
      author="Yuchen Jin <cainmagi@gmail.com>" \
      description="A python tool for synchronize the messages from different threads, processes or hosts." \
      version="1.2.0"

# Set configs
ARG INSTALL_MODE=default
# The following args are temporary but necessary during the deployment.
# Do not change them.
ARG DEBIAN_FRONTEND=noninteractive

# Force the user to be root
USER root

# Import the installation scripts earlier, this may help improve the
# reusablitity of the cached layers.
WORKDIR /app
COPY ./docker/* /app/
COPY ./*.* /app/
COPY ./syncstream /app/syncstream
COPY ./version /app/version
COPY ./tests /app/tests

# Install dependencies
RUN bash /app/install.sh $INSTALL_MODE

ENTRYPOINT ["bash", "--login", "./docker-entrypoint.sh"]
CMD [""]
