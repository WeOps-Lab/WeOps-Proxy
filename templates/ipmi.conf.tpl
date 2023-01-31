{{ $zone := envOrDefault "ZONE" "default" }}
modules:
{{ range ls (printf "/weops/zone/%s/ipmi" $zone) }}{{ with $d := .Value | parseYAML }}
  {{ $d.name }}:
    user: "{{ $d.user }}"
    password: "{{ $d.password }}"
    driver: "{{ $d.driver }}"
    timeout: 10000
    collectors:
    - bmc
    - ipmi
    - chassis
    - dcmi
    - sel
    - sm-lan-mode{{end}}{{end}}
