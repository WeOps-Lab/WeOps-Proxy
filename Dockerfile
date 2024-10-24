FROM alpine:3.17
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/' /etc/apk/repositories && \
apk add supervisor freeipmi curl vim ipmitool && \
adduser weops --uid 1001 --disabled-password && \
mkdir /var/log/supervisor && chown 1001:1001 /var/log/supervisor && \
mkdir -p /app/run && chown 1001:1001 /app/run && \
mkdir -p /app/log && chown 1001:1001 /app/log && \
mkdir /lib64 && ln -s /lib/ld-musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2
WORKDIR /app
ADD ./config ./config
ADD ./templates ./templates

ENV PROXY_HOME /app
ENV ENV_CONSUL_ADDR http://127.0.0.1:8501
ENV IPMI_RUNTIME ipmi_exporter
RUN  wget -O /tmp/consul.zip https://releases.hashicorp.com/consul/1.14.1/consul_1.14.1_linux_amd64.zip && unzip -d /bin /tmp/consul.zip && \ 
wget -O /tmp/consul-template.zip https://releases.hashicorp.com/consul-template/0.29.5/consul-template_0.29.5_linux_amd64.zip && unzip -d /bin /tmp/consul-template.zip && \
wget -O /tmp/grafana-agent.zip https://github.com/grafana/agent/releases/download/v0.30.1/agent-linux-amd64.zip && unzip -d /bin /tmp/grafana-agent.zip && mv /bin/agent-linux-amd64 /bin/grafana-agent && \
wget -O /tmp/telegraf.tar.gz https://dl.influxdata.com/telegraf/releases/telegraf-1.25.0_linux_amd64.tar.gz && tar -zxvf /tmp/telegraf.tar.gz -C /app && ln -s /app/telegraf-1.25.0/usr/bin/telegraf /bin && \
wget -O /tmp/ipmi.tar.gz https://github.com/prometheus-community/ipmi_exporter/releases/download/v1.6.1/ipmi_exporter-1.6.1.linux-amd64.tar.gz && cd /tmp && tar -zxvf ipmi.tar.gz && cp /tmp/ipmi_exporter-1.6.1.linux-amd64/ipmi_exporter /bin &&\
rm -rf /tmp/* && \
chown -R 1001:1001 /app

USER weops
EXPOSE 12345
ENTRYPOINT ["docker-entrypoint.sh"]  