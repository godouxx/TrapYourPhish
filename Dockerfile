FROM rust:latest as build

# create a new empty shell project
RUN USER=root cargo new --bin web_website
WORKDIR /web_website

# copy over your manifests
COPY ./Backend/Cargo.lock ./Cargo.lock
COPY ./Backend/Cargo.toml ./Cargo.toml

# this build step will cache your dependencies
RUN cargo build --release
RUN rm src/*.rs

# copy your source tree
COPY ./Backend/src ./src

# build for release
RUN rm ./target/release/deps/web_website*
RUN cargo build --release

# our final base
FROM debian:latest

## install the runtime dependencies
RUN apt-get update

# Install libc
RUN apt-get install -y libc6 ca-certificates tzdata python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Cleanup
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# set the timezone
ENV TZ=Europe/Paris

# set the working directory in the image
WORKDIR /web_website

# copy the build artifact from the build stage
COPY --from=build /web_website/target/release/web_website .

# copy the assets, html, utils folder to the final image
COPY ./Backend/assets ./assets
COPY ./Backend/html ./html
COPY ./Backend/utils ./utils
COPY ./Backend/config ./config

# Setup python env for predicting mail
COPY ./requirements.txt ./requirements.txt
RUN python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# copy the models and predict file
RUN mkdir -p mail
COPY ./ML/mail/cleaner.py ./mail/cleaner.py
COPY ./ML/predict.py ./predict.py

RUN mkdir -p models/url
COPY ./models/opti_svm_mail.pkl ./models/opti_svm_mail.pkl
COPY ./models/opti_tfidf_mail.pkl ./models/opti_tfidf_mail.pkl

COPY ./models/url/bow_Random_Forest.pkl ./models/url/bow_Random_Forest.pkl
COPY ./models/url/bow_vectorizer.pkl ./models/url/bow_vectorizer.pkl

RUN sed -i "s|\"python_filepath\": \".*\"|\"python_filepath\": \".venv/bin/python3\"|" config/default.json
RUN sed -i "s|\"predict_filepath\": \".*\"|\"predict_filepath\": \"predict.py\"|" config/default.json
RUN sed -i "s|\"db_host\": \".*\"|\"db_host\": \"mysql\"|" config/default.json
RUN sed -i 's|\.\./models|models|g' predict.py

# set the startup command to run your binary
CMD ["./web_website", "--prod"]
