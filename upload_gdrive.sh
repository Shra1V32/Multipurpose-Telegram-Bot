#!/bin/bash
# This script enables the user to upload a file to Google Drive
# fail fast

# extract access_token value from the json response using jq
#ACCESS_TOKEN=`echo $BEARER | jq -r '.access_token'`
#echo $ACCESS_TOKEN
# filename="$1"
# # echo $filename
# mime_type="$(file -b --mime-type "$1")"
# ACCESS_TOKEN=$(cat gdrivetoken)
# # echo $mime_type $filename
# echo $(./bin//usr/bin/curl -X POST -L -H 'Authorization: Bearer '${ACCESS_TOKEN} \
#     -H "Transfer-Encoding: chunked" \
#     -F "metadata={name : \"$filename\", parents : [\"1v3JeNCu3Ylf8AiogMf5ulKa_y74zhpyg\"]};type=application/json;charset=UTF-8" \
#     -F "file=@$filename;type=${mime_type}" \
#     'https://www.googleapis.com/upload/drive/v3/files?uploadType=')
filename="$(printf "$1")"
file_type=$(file -b --mime-type "$filename")
FILE_SIZE=$(ls -l "$(echo "$filename" | tr -d \\)" | cut -f5 -d\ )
ACCESS_TOKEN=$(cat gdrivetoken)
epoch=$(date +%s)
echo $filename $1 $FILE_SIZE "'$(echo "$filename" | sed 's/\[/\\[/g; s/\]/\\]/g')'"
curl -v -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "X-Upload-Content-Type: $file_type" \
  -H "X-Upload-Content-Length: $FILE_SIZE" \
  -d "{\"name\": '$1', 'parents':['1v3JeNCu3Ylf8AiogMf5ulKa_y74zhpyg']}" \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable" > "$epoch.tmp" 2>&1
dos2unix "$epoch.tmp" >> /dev/null 2>&1
GURL="`cat "$epoch.tmp" |grep 'location: ' | cut -f3 -d\ `"
rm "$epoch.tmp"
# echo "${GURL}"
echo `curl -g -X PUT -H "Content-Type: application/octet-stream" -T "$filename" "$GURL"`

