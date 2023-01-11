{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}{{ $zone := envOrDefault "ZONE" "default" }}prometheus.remote_write "staging" {
  endpoint {
    url = {{ $remote_url }}

 #   http_client_config {
 #     basic_auth {
 #       username = "admin"
 #       password = "admin"
      }
    }
  }
}


{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}
prometheus.scrape "{{$d.name}}" {
  targets = [
    {"__address__" = "localhost:12345", "instance" = "{{$d.address}}"},
  ]

  forward_to = [prometheus.remote_write.staging.receiver]

  scrape_interval = "{{$d.interval}}"
  scrape_timeout = "{{$d.timeout}}"
  params          = { "target" = ["{{$d.address}}"], "module" = ["{{$d.module}}"], "walk_params" = ["{{$d.walk_params}}"] }
  metrics_path    = "/integrations/snmp/metrics"
}{{ end }}{{ end }}

logging {
  level  = "info"
  format = "logfmt"
}