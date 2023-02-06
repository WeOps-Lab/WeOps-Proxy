{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}{{ $zone := envOrDefault "ZONE" "default" }}prometheus.remote_write "staging" {
  endpoint {
    url = "{{ $remote_url }}"
  }
}


{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}prometheus.scrape "{{$d.name}}" {
  targets = [
    {"__address__" = "localhost:12345", "instance" = "{{$d.address}}", "module" = "{{$d.module}}"},
  ]

  forward_to = [prometheus.relabel.init_proxy_label.receiver]

  scrape_interval = "{{$d.interval}}"
  scrape_timeout = "{{$d.timeout}}"
  params          = { "target" = ["{{$d.address}}"], "module" = ["{{$d.module}}"], "walk_params" = ["{{$d.walk_params}}"] }
  metrics_path    = "/integrations/snmp/metrics"
}{{ end }}
{{ end }}

{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}prometheus.scrape "{{$d.name}}" {
  targets = [
    {"__address__" = "localhost:9290", "instance" = "{{$d.task.address}}", "module" = "{{$d.name}}"},
  ]

  forward_to = [prometheus.relabel.init_proxy_label.receiver]

  scrape_interval = "{{$d.scrape_interval}}"
  scrape_timeout = "{{$d.scrape_timeout}}"
  params          = { "target" = ["{{$d.task.address}}"], "module" = ["{{$d.name}}"] }
  metrics_path    = "/ipmi"
}{{ end }}
{{ end }}

prometheus.relabel "init_proxy_label" {
  forward_to = [prometheus.remote_write.staging.receiver]

  rule {
    action        = "replace"
    target_label  = "zone"
    replacement   = "{{ $zone }}"
  }

  rule {
    action        = "replace"
    target_label  = "source"
    replacement   = "weops_proxy"
  }
}

logging {
  level  = "info"
  format = "logfmt"
}