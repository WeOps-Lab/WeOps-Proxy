{{ $remote_url := envOrDefault "REMOTE_URL" "http://10.10.10.10/api/v1/write" }}
{{ $zone := envOrDefault "ZONE" "default" }}metrics:
  wal_directory: /tmp/wal
  global:
    scrape_interval: 15s
    remote_write:
    - url: {{ $remote_url }}

    external_labels:
      source: weops_proxy
      zone: default
integrations:
  snmp:
    enabled: true
    config_file: /app/config/modules.yaml
    relabel_configs:
    - source_labels: ["__param_module"]
      target_label: module
    snmp_targets:
{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}{{ $d.target | indent 4 }}{{ end }}{{ end }}
    walk_params:
{{ range ls (printf "/weops/zone/%s/snmp" $zone) }}{{ with $d := .Value | parseYAML }}{{ $d.param | indent 5 }}
{{ end }}{{ end }}