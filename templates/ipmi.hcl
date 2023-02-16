template {
  source = "/app/templates/ipmi.conf.tpl"
  destination = "/app/config/ipmi.conf"
  command = "sh -c 'supervisorctl -c /app/config/supervisord.conf  restart ipmi'"
}