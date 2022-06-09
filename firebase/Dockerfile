FROM node:14-alpine
RUN npm install firebase-functions@latest firebase-admin@latest --save
RUN npm install -g firebase-tools
COPY . /firebase
RUN cd firebase/functions && npm install
WORKDIR /firebase/
