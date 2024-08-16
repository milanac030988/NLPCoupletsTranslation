#!/bin/bash

# Lấy đường dẫn của thư mục chứa script đang chạy
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

export RAW_DATA_DIR="$SCRIPT_DIR/data/raw"
export PROCESS_DATA_DIR="$SCRIPT_DIR/data/processed"
export INTERMEDIATE_DATA_DIR="$SCRIPT_DIR/data/interim"
export REFS_DIR="$SCRIPT_DIR/references"
export MOSSES_DECODER="$SCRIPT_DIR/references/mossesdecoder"
export MODELS_DIR="$SCRIPT_DIR/models"
export PYTHON=python3

# Kiểm tra giá trị của các biến
echo "SCRIPT_DIR: $SCRIPT_DIR"
echo "RAW_DATA_DIR: $RAW_DATA_DIR"
echo "PROCESS_DATA_DIR: $PROCESS_DATA_DIR"
echo "INTERMEDIATE_DATA_DIR: $INTERMEDIATE_DATA_DIR"
echo "REFS_DIR: $REFS_DIR"
echo "MOSSES_DECODER: $MOSSES_DECODER"
echo "PYTHON: $PYTHON"