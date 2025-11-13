#!/bin/bash

# Set source directory (default to raw/ if no argument provided)
source_dir="${1:-raw}"

# Set destination directory (default to ORD_files if no second argument provided)
dest_dir="$source_dir/${2:-ORD_files}"

# Create destination directory if it doesn't exist
mkdir -p "$dest_dir"

# Process each zip file in source directory
for zip_file in "$source_dir"/*.zip; do
    if [ -f "$zip_file" ]; then
        echo "Processing $zip_file..."

        # Extract zip file in place
        unzip -q "$zip_file" -d "$source_dir"/

        # Get the extracted directory name (without .zip extension)
        dir_name=$(basename "$zip_file" .zip)

        # Rsync contents of extracted directory to destination
        if [ -d "$source_dir/$dir_name" ]; then
            # For "ORD files - YYYYMMDD" pattern, process only Contribute/Establish/Explore subdirectories
            if echo "$dir_name" | grep -q "^ORD files - "; then
                for subdir in "$source_dir/$dir_name"/*/; do
                    if [ -d "$subdir" ]; then
                        subdir_name=$(basename "$subdir")
                        # Only process directories that start with Contribute, Establish, or Explore
                        if echo "$subdir_name" | grep -q "^Contribute\|^Establish\|^Explore"; then
                            base_name=$(echo "$subdir_name" | cut -d' ' -f1)
                            rsync -r "$subdir" "$dest_dir/$base_name"/
                            echo "Synced contents of $subdir_name to $dest_dir/$base_name"
                        fi
                    fi
                done
            # For other directories with " - " pattern, extract base name
            elif echo "$dir_name" | grep -q " - "; then
                base_name=$(echo "$dir_name" | cut -d' ' -f1)
                rsync -r "$source_dir/$dir_name"/ "$dest_dir/$base_name"/
                echo "Synced contents of $dir_name to $dest_dir/$base_name"
            else
                rsync -r "$source_dir/$dir_name"/ "$dest_dir"/
                echo "Synced contents of $dir_name to $dest_dir"
            fi

            # Remove the extracted directory after rsync
            rm -rf "$source_dir/$dir_name"
            echo "Removed extracted directory $dir_name"
        fi
    fi
done

echo "All zip files processed and contents synced to $dest_dir"