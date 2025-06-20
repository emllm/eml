#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EML_FILE="$SCRIPT_DIR/testapp.eml.sh"

# Extract and run the script part (skip email headers)
{
    # Skip email headers
    while IFS= read -r line; do
        if [[ "$line" == '#!/bin/bash'* ]]; then
            echo "$line"
            break
        fi
    done < "$EML_FILE"
    
    # Output the rest of the file
    tail -n +$(grep -n '^#!\?/bin/bash' "$EML_FILE" | cut -d: -f1) "$EML_FILE"
} | bash -s -- "$@"
