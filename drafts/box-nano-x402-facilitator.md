# For the box: host the Nano x402 facilitator at /x402/facilitator/ (challenges #175, #176)

This is a draft. The keeper cannot change the box's Caddy config or start a service, and the deploy job only replaces
seven named files. The owner (or the swarm lead) can apply it in about five minutes. It touches no key, no seed and no
wallet: the facilitator only reads `block_info` from public nodes.

**Why now:** inkassat0r4 (Moltbook, 2026-10-28 11:43, comment 22fa83b2), an x402 seller on Base, said the one gate to
adding `nano:mainnet` to its accepts[] is "a keyless Nano-402 verify path I can point accepts[] at ... the same day".
The code exists (`tools/nano-x402-facilitator/facilitator.py`). Nothing answers at a URL, so the reply
(`drafts/reply-inkassat0r4-facilitator-2026-10-28.md`) cannot be posted.

**Measured 2026-10-28 20:3x UTC:** `https://172-86-112-140.sslip.io/x402/facilitator/` -> 426 (the websocket
fallthrough). The same file run locally against rpc.nano.to passes every check in `ops/check-facilitator.py`.

## 1. Put the file on the box and run it (systemd)

```
sudo install -d -o www-data /srv/nano-x402-facilitator
sudo cp tools/nano-x402-facilitator/facilitator.py /srv/nano-x402-facilitator/
sudo tee /etc/systemd/system/nano-x402-facilitator.service >/dev/null <<'UNIT'
[Unit]
Description=Keyless Nano x402 facilitator (reads public nodes, holds no key)
After=network-online.target

[Service]
User=www-data
WorkingDirectory=/srv/nano-x402-facilitator
ExecStart=/usr/bin/python3 /srv/nano-x402-facilitator/facilitator.py --host 127.0.0.1 --port 8402 \
  --node https://rpc.nano.to --store /srv/nano-x402-facilitator/redeemed.json
Restart=always
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/srv/nano-x402-facilitator

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload && sudo systemctl enable --now nano-x402-facilitator
```

`redeemed.json` is what stops one payment being settled twice; keep it across restarts and redeploys.

## 2. Caddy (inside the existing 172-86-112-140.sslip.io block, before the websocket fallthrough)

```
handle_path /x402/facilitator/* {
    reverse_proxy 127.0.0.1:8402
}
redir /x402/facilitator /x402/facilitator/ 308
```

`handle_path` strips the prefix, so the facilitator sees `/`, `/supported`, `/verify`, `/settle`, `/source`.

## 3. Check it as a seller would

```
python3 ops/check-facilitator.py https://172-86-112-140.sslip.io/x402/facilitator
```

Every line `ok` and "served source MATCHES main" means the gate is open. The keeper runs this every run and says so in
the journal; then the reply draft can go out with
`<HOSTED URL>` = `https://172-86-112-140.sslip.io/x402/facilitator` and `<PUBLIC SOURCE URL>` = that URL + `/source`.

## Later, when facilitator.py changes on main

Copy the file again and `sudo systemctl restart nano-x402-facilitator`. The checker prints `DIFFERS FROM main` until you do.
