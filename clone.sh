token=$(cat gdrivetoken)
curl --request POST \
  --header 'Authorization: Bearer '$token \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --url 'https://www.googleapis.com/drive/v3/files/1Y0pCDC6Xw194Zr1tm-qiKbCDJduMVMrX/copy?supportsAllDrives=true'
