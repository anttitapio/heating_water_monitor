#!/usr/bin/env bash

if [ $# -ne 2 ]
  then
    echo "Usage: $0 <gmail account name for mail sending> <gmail pw>"
    exit
fi
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
apt-get install -y python3-pip
pip3 install yagmail systemd

cat > /lib/systemd/system/tempread.service <<EOF
[Unit]
Description=DS1820 Temp reader
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 $DIR/tempRead.py
StandardInput=tty-force
Environment="GM_USER=${1}"
Environment="GM_PASS=${2}"

[Install]
WantedBy=multi-user.target
EOF
echo ''
echo 'To finish setup, add alarm mail recipients (one mail address per line) in <script dir>/mail_recipients.txt'
echo 'Then enable and start the service with:'
echo 'sudo systemctl enable tempread'
echo 'sudo systemctl start tempread'

