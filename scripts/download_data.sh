#!/bin/bash

# Directory to store downloaded data
DATA_DIR="./data/raw"

# Check if Kaggle CLI is installed
if ! command -v kaggle &> /dev/null
then
    echo "❌ Kaggle CLI is not installed! Please install it using:"
    echo "   pip install kaggle"
    exit 1
fi

# Check if Kaggle API Key is set up
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ Kaggle API Key is missing! Please download the API key from Kaggle and place it in ~/.kaggle/kaggle.json"
    exit 1
fi

# Create the storage directory if it does not exist
mkdir -p $DATA_DIR

# Download data from Kaggle
echo "🚀 Downloading data from Kaggle..."
kaggle competitions download -c child-mind-institute-detect-sleep-states -p $DATA_DIR

# Unzip the downloaded file if it exists
echo "📦 Extracting data..."
unzip -o "$DATA_DIR/child-mind-institute-detect-sleep-states.zip" -d $DATA_DIR

# Remove the ZIP file after extraction
rm "$DATA_DIR/child-mind-institute-detect-sleep-states.zip"

echo "✅ Data has been successfully downloaded and extracted to: $DATA_DIR"
