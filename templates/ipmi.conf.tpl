{{ $zone := envOrDefault "ZONE" "default" }}
modules:
{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}
  {{ $d.name }}:
    user: "{{ $d.task.user }}"
    pass: "{{ $d.task.pass }}"
    driver: "{{ $d.task.driver }}"
    timeout: {{ $d.task.timeout }}
    collectors:
    - bmc
    - ipmi
    - chassis
    - dcmi
    - sel
    - sm-lan-mode{{end}}{{end}}
