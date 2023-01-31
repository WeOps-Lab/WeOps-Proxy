{{ $zone := envOrDefault "ZONE" "default" }}
modules:
{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}
  {{ $d.name }}:
    user: "{{ $d.user }}"
    password: "{{ $d.password }}"
    driveer: "{{ $d.driver }}"
    timeout: {{ $d.timeout }}
    collectors:
    - bmc
    - ipmi
    - chassis
    - dcmi
    - sel
    - sm-lan-mode{{end}}{{end}}
