FROM alpine:latest
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/' /etc/apk/repositories
RUN apk add supervisor
RUN adduser weops --uid 1001 --disabled-password
RUN mkdir /var/log/supervisor && chown 1001:1001 /var/log/supervisor
RUN mkdir -p /app/run && chown 1001:1001 /app/run
RUN mkdir -p /app/log && chown 1001:1001 /app/log
RUN mkdir /lib64 && ln -s /lib/ld-musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2
WORKDIR /app
ADD ./config ./config
ADD ./templates ./templates
RUN chown -R 1001:1001 /app

ENV PROXY_HOME /app
RUN wget -O /tmp/consul.zip https://releases.hashicorp.com/consul-template/0.29.5/consul-template_0.29.5_linux_amd64.zip && unzip -d /bin /tmp/consul.zip
RUN wget -O /tmp/grafana-agent.zip https://github.com/grafana/agent/releases/download/v0.28.0/agent-linux-amd64.zip && unzip -d /bin /tmp/grafana-agent.zip && mv /bin/agent-linux-amd64 /bin/grafana-agent
RUN rm -rf /tmp/*.zip
RUN chown -R 1001:1001 /app 

USER weops
EXPOSE 12345
ENTRYPOINT ["supervisord","-c","config/supervisord.conf","--nodaemon"]
