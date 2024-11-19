#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 NEW_NAME"
  exit 1
fi

# New name to replace '__SERVICE_NAME__'
NEW_NAME=$1

# Iterate through all files recursively in the current directory, excluding .sh files
find "$(pwd)" -type f ! -name "*.sh" | while IFS= read -r file; do
  # Set the appropriate locale for character encoding handling
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS variant: uses LC_CTYPE and requires a .bak extension for inline replacement
    LC_CTYPE=C sed -i .bak "s/__SERVICE_NAME__/$NEW_NAME/g" "$file" && rm "${file}.bak"
  else
    # Linux variant: uses LC_ALL without needing a backup extension
    LC_ALL=C sed -i "s/__SERVICE_NAME__/$NEW_NAME/g" "$file"
  fi
done
