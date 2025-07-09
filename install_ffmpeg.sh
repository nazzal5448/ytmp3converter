#!/bin/bash

# Exit if already installed
if [ -f "/usr/local/bin/ffmpeg" ]; then
  echo "FFmpeg already installed"
  exit 0
fi

echo "Installing FFmpeg..."

# Download and extract static ffmpeg build
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
cd ffmpeg-*-amd64-static

# Move ffmpeg and ffprobe to /usr/local/bin
mv ffmpeg ffprobe /usr/local/bin/

# Clean up
cd ..
rm -rf ffmpeg-*-amd64-static ffmpeg.tar.xz

echo "FFmpeg installation completed."
