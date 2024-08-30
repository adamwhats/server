# Goosenet Server
Documentation and scripts related with my home server, which runs Debian 12 on a small i5 machine. 

## Local

TODO
local DNS
rsnapshot
updating

## Remote

### Domain name
The domain name is `goosenet.cloud` which is registered through [Namecheap](https://www.namecheap.com/).

### DNS
DNS is hosted/managed by [DeSEC.io](https://desec.io/). This provides the nameservers, DNSSEC and an API which allows the server to dynamically configure settings. The token for the API is stored in the `DESEC_TOKEN` environment variable.

The server runs a [script](./update_dns_ip.py) (managed through cron) which finds the current dynamic public IP adress and updates the DeSEC using the API. 