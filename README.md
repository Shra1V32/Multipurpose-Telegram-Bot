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

## Requirements
- Python (version 3.11)
- A Linux Machine (For all the features to work)

## Usage

1. Clone this repository to your local machine.

2. Configure the necessary API credentials in the `constants.py` file.

3. Install required dependencies using the commands provided below:
```shell
sudo ./setup.sh
```

4. Interact with the bot through Telegram using the provided commands.
```shell
./aria.sh
python3.11 ./main.py
```

## Credits
- Telethon
- Aria
- yt-dlp
