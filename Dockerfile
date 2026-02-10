# MyFaba Hacks - Docker Image
# Provides a containerized environment for creating custom Faba figures
# without needing to install Java or id3v2 locally

FROM debian:bullseye-slim

# Add metadata labels
LABEL maintainer="MyFaba Hacks Project"
LABEL description="Docker container for creating custom MyFaba audio figures"
LABEL version="1.0"

# Install required dependencies
# - bash: Shell script execution
# - id3v2: MP3 tag manipulation
# - openjdk-17: Java runtime and development kit for cipher tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    id3v2 \
    openjdk-17-jre \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy necessary files into the container
COPY createFigure.sh /app/createFigure.sh
COPY MKICipher.java /app/MKICipher.java
COPY MKIDecipher.java /app/MKIDecipher.java

# Make the shell script executable
RUN chmod +x /app/createFigure.sh

# Compile Java cipher/decipher tools
RUN javac MKICipher.java MKIDecipher.java

# Set the entrypoint to run the createFigure script
# Usage: docker run --rm -v /path/to/songs:/source-folder createfigure-image <figure_id> /source-folder
ENTRYPOINT ["/bin/bash", "/app/createFigure.sh"]

