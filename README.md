# Telethon-based Telegram File Bot
## A Mini-Project done by 2nd Year IT Student
## Awarded 1st Prize in Project Expo, MVSREC - Dept. of IT 

## PRs are always welcome
## Key Features

- **File Downloading:** Users can initiate file downloads by sending a command with a valid URL or magnet link. The bot manages the download queue and provides real-time progress updates.

- **YouTube Video Download:** The bot supports YouTube video downloads, allowing users to quickly save YouTube videos to their Google Drive.

- **PDF Conversion:** Users can convert PDF files to a series of images and vice versa. The bot handles this conversion seamlessly.

- **Quote Generator:** The bot can generate random quotes from the ZenQuotes API, providing users with inspirational and thought-provoking messages.

- **File Cloning:** It offers the ability to clone files, providing a new link to the same content hosted on Google Drive.

- **Command Interface:** Users can interact with the bot through various commands, each serving a specific purpose. A `/help` command is available to list all available commands and their descriptions.

- **Ping Test:** The bot can perform a ping test to check network connectivity and respond with the results.

- **Voice-to-Text Conversion:** Users can tag voice messages, and the bot will analyze the audio to provide a text transcription.

## Commands
1. `/dl [URL]`: Download and upload a file directly to Google Drive. Replace `[URL]` with the URL of the file you want to download.

2. `/ytdl [YouTube URL]`: Download a YouTube video and upload it to Google Drive. Replace `[YouTube URL]` with the URL of the YouTube video.

3. `/convert`: Convert the sent images into a single PDF.

4. `/pdf2img`: Convert a tagged PDF file into a series of images.

5. `/img2pdf`: Prepare images for conversion to PDF. This command is used to collect images for later conversion.

6. `/cancel [GID]`: Cancel a specific download or upload by specifying its GID (Group ID).

7. `/cancelall`: Cancel all ongoing downloads and uploads.

8. `/start`: Check if the bot is running.

9. `/quote`: Fetch a random quote.

10. `/run [command]`: Execute shell commands (only authorized users). Replace `[command]` with the command you want to run.

11. `/ping`: Check the bot's network latency.

12. `/help`: Display a list of available commands and their descriptions.

13. `/voice2text`: Convert a tagged voice message to text.


## Requirements
- Python (version 3.11)
- A Linux Machine (For all the features to work)

## Retrieving API Hash Values

### Telegram

To retrieve the API hash value from Telegram, follow these steps:

1. Visit [Telegram's API development tools](https://my.telegram.org/apps).
2. Log in with your Telegram account. Note: You'll receive a code in your Telegram messages.
3. After logging in, click on 'API development tools'.
4. Fill in the required fields. If you're not sure about these fields, you can enter dummy data.
5. After filling in the details, you'll be provided with the 'API_ID' and 'API_HASH'. Keep these safe.

### Google Drive

To retrieve the API hash value from Google Drive, follow these steps:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Go to 'APIs & Services' > 'Library'.
4. Search for 'Google Drive API' and enable it for your project.
5. Go to 'APIs & Services' > 'Credentials'.
6. Click on 'Create Credentials' > 'API key'. Your API key will be displayed. Keep it safe.
7. For the Client ID, click on 'Create Credentials' > 'OAuth client ID'.
8. Configure the OAuth consent screen if required.
9. For 'Application type', select 'Web application'.
10. Enter a name, and under 'Authorized redirect URIs', add 'https://developers.google.com/oauthplayground'.
11. Click 'Create'. Your client ID will be displayed. Keep it safe.
12. Open the downloaded credentials file and fill in the details as required in `constats.py`

## Usage

1. Clone this repository to your local machine.

2. Configure the API_ID, API_HASH, and BOT_TOKEN in the `constants.py` with your values.

3. Install required dependencies using the commands provided below:
```shell
sudo ./setup.sh
```

4. Interact with the bot through Telegram using the provided commands.
```shell
python3.11 ./main.py
```

## Credits
- Telethon
- Aria
- yt-dlp
