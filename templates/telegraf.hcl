template {
  source = "/app/templates/telegraf.conf.tpl"
  destination = "/app/config/telegraf.conf"
  command = "sh -c 'supervisorctl -c /app/config/supervisord.conf  restart telegraf'"
}