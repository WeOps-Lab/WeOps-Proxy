template {
  source = "/app/templates/flow.conf.tpl"
  destination = "/app/config/flow.conf"
  command = "curl http://127.0.0.1:1234/-/reload || echo panic"
}