# OSXPhotos Scripts

This repository contains utility scripts for working with the Photos library on macOS using the [osxphotos](https://github.com/RhetTbull/osxphotos) package.

## Photo Cluster Finder

The `find_photo_clusters.py` script identifies and organizes clusters of photos taken within a specified time window. This is useful for finding burst shots or series of related photos taken in sequence.

### Features

- Identifies groups of photos taken within a customizable time window
- Creates albums or sub-albums to organize the clustered photos
- Interactive command-line interface with sensible defaults
- Customizable minimum cluster size
- Support for nested album organization

### Requirements

- Python 3.6+
- osxphotos package
- macOS with Photos app

### Installation

1. Install the osxphotos package:
   ```bash
   uv pip install osxphotos
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/jdreimann/osxphotos-scripts.git
   cd osxphotos-scripts
   ```

### Usage

Run the script with the osxphotos command-line tool:

```bash
osxphotos run find_photo_clusters.py
```

The script will prompt you for the following parameters:

1. **Time Window**: The maximum time gap between photos to be considered part of the same cluster (default: "1 min")
   - Format examples: "30 sec", "1.5 min", "1 hour"

2. **Album Name**: The name of the album to create with clustered photos (default: "Photo Clusters")

3. **Minimum Cluster Size**: The minimum number of photos required to form a cluster (default: 10)

4. **Create Sub-Albums**: Whether to create sub-albums for each cluster (default: Yes)
   - If Yes, creates a parent album with nested sub-albums for each cluster
   - If No, adds all clustered photos to a single album

### Example

Using the default settings, the script will:
1. Find all clusters of photos taken within 1 minute of each other
2. Create a main album called "Photo Clusters" 
3. Create sub-albums for each cluster named "Cluster X (YYYY-MM-DD HH:MM:SS)"
4. Only include clusters with 10 or more photos

### Tips

- For burst shots, try a smaller time window (e.g., "5 sec")
- For event grouping, try a larger window (e.g., "5 min" or "10 min")
- You can customize the minimum cluster size based on your needs (smaller value = more clusters)

## License

MIT