filename="$1"
file_type=$(file -b --mime-type "$1")
FILE_SIZE=$(ls -l "$1" | cut -f5 -d\ )
ACCESS_TOKEN=$(cat gdrivetoken)
echo `
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "X-Upload-Content-Type: $file_type" \
  -H "X-Upload-Content-Length: $FILE_SIZE" \
  -d "{\"name\": \"$filename\"}" \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"`
