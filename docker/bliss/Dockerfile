FROM alpine:3.14

ENV VMARGS -Dbliss_working_directory=/config

EXPOSE 3220 3221

RUN mkdir /bliss

RUN apk update
RUN apk add wget openjdk8-jre-base bash

RUN wget -qO- http://www.blisshq.com/app/latest-linux-version | xargs wget -O bliss-install-latest.jar -nv

RUN echo INSTALL_PATH=/bliss > auto-install.properties
RUN java -jar bliss-install-latest.jar -console -options auto-install.properties

WORKDIR /bliss

CMD /bliss/bin/bliss.sh

