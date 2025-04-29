#!/usr/bin/env python3
"""
Find clusters of photos taken within a specified time window of each other and add them to an album.

Usage:
    osxphotos run find_photo_clusters.py --window "1 min" --album "Photo Clusters"
"""

import datetime
import sys
import click
from typing import List

import osxphotos
from osxphotos.cli import query_command, verbose
from osxphotos.photosalbum import PhotosAlbum


def parse_time_delta(time_delta_str: str) -> datetime.timedelta:
    """Parse a time delta string into a datetime.timedelta object.
    
    Accepts formats like "1 min", "30 sec", "1 hour", "1.5 min", etc.
    """
    time_delta_str = time_delta_str.lower().strip()
    
    # Extract numeric part and unit
    parts = time_delta_str.split(maxsplit=1)
    
    if len(parts) == 0:
        raise ValueError(f"Could not parse time delta: {time_delta_str}")
    
    try:
        # Use float instead of int to handle decimal values
        value = float(parts[0])
    except ValueError:
        raise ValueError(f"Could not parse numeric value in time delta: {time_delta_str}")
    
    unit = parts[1] if len(parts) > 1 else ""
    
    # Handle various time formats
    if unit.startswith("sec"):
        return datetime.timedelta(seconds=value)
    elif unit.startswith("min"):
        return datetime.timedelta(minutes=value)
    elif unit.startswith("hour") or unit.startswith("hr"):
        return datetime.timedelta(hours=value)
    else:
        # Try to parse as seconds if no unit specified
        return datetime.timedelta(seconds=value)

def find_clusters(photos: List[osxphotos.PhotoInfo], 
                  time_window: datetime.timedelta) -> List[List[osxphotos.PhotoInfo]]:
    """Find clusters of photos taken within time_window of each other."""
    if not photos:
        return []
    
    # Filter out photos with None dates
    valid_photos = [p for p in photos if p.date is not None]
    if not valid_photos:
        return []
    
    # Sort photos by date
    sorted_photos = sorted(valid_photos, key=lambda p: p.date)
    
    # Improved clustering algorithm that looks at all photos within the time window
    # not just adjacent ones
    clusters = []
    i = 0
    
    verbose("Starting photo clustering analysis...")
    
    while i < len(sorted_photos):
        current_photo = sorted_photos[i]
        verbose(f"Considering photo: timestamp={current_photo.date}, "
                f"name={current_photo.filename}, "
                f"size={current_photo.original_filesize:,} bytes")
        
        # Start a new cluster with the current photo
        current_cluster = [current_photo]
        cluster_end_time = current_photo.date + time_window
        
        # Find all photos that fall within the time window of the cluster
        j = i + 1
        while j < len(sorted_photos) and sorted_photos[j].date <= cluster_end_time:
            next_photo = sorted_photos[j]
            verbose(f"  Adding to cluster: timestamp={next_photo.date}, "
                    f"name={next_photo.filename}, "
                    f"size={next_photo.original_filesize:,} bytes")
            
            current_cluster.append(next_photo)
            # Extend the cluster end time if we find a new photo within the window
            cluster_end_time = max(cluster_end_time, next_photo.date + time_window)
            j += 1
        
        # Save the cluster if it has more than one photo
        if len(current_cluster) > 1:
            verbose(f"Found cluster with {len(current_cluster)} photos")
            clusters.append(current_cluster)
            i = j  # Skip to the first photo after this cluster
        else:
            verbose("Photo does not belong to any cluster")
            i += 1  # Move to the next photo
    
    return clusters

@query_command()
def main(photos: List[osxphotos.PhotoInfo], **kwargs):
    """Find clusters of photos taken within a specified time window of each other and add them to an album."""
    # Interactive mode: prompt for each option with default values
    click.echo("\nPhoto Clustering Tool\n")
    
    # Default values
    default_window = "1 min"
    default_album = "Photo Clusters"
    default_min_cluster_size = 10
    default_create_sub_albums = True
    
    # Prompt for time window
    window_prompt = click.style(f"Time window for clustering photos [default: {default_window}]: ", fg="green")
    window = click.prompt(window_prompt, default=default_window, show_default=False)
    
    # Prompt for album name
    album_prompt = click.style(f"Album name [default: {default_album}]: ", fg="green")
    album = click.prompt(album_prompt, default=default_album, show_default=False)
    
    # Prompt for minimum cluster size
    min_cluster_size_prompt = click.style(f"Minimum number of photos in a cluster [default: {default_min_cluster_size}]: ", fg="green")
    min_cluster_size = click.prompt(min_cluster_size_prompt, default=default_min_cluster_size, show_default=False, type=int)
    
    # Prompt for create sub-albums
    create_sub_albums_prompt = click.style(f"Create sub-albums for each cluster [default: {'Yes' if default_create_sub_albums else 'No'}]: ", fg="green")
    create_sub_albums_str = click.prompt(create_sub_albums_prompt, default="Yes" if default_create_sub_albums else "No", show_default=False)
    create_sub_albums = create_sub_albums_str.lower() in ("yes", "y", "true", "t", "1")
        
    verbose(f"Found {len(photos)} photos")
    verbose(f"Finding photo clusters with time window: {window}")

    try:
        time_window = parse_time_delta(window)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # Find clusters
    clusters = find_clusters(photos, time_window)
    
    # Filter clusters based on minimum size
    clusters = [cluster for cluster in clusters if len(cluster) >= min_cluster_size]
    
    verbose(f"Found {len(clusters)} clusters with at least {min_cluster_size} photos")
    
    if not clusters:
        click.echo("No photo clusters found.")
        return
    
    # Print cluster info
    for i, cluster in enumerate(clusters):
        cluster_start = min(p.date for p in cluster)
        cluster_end = max(p.date for p in cluster)
        duration = cluster_end - cluster_start
        
        verbose(f"Cluster {i+1}: {len(cluster)} photos, " 
                f"from {cluster_start.strftime('%Y-%m-%d %H:%M:%S')} "
                f"to {cluster_end.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(duration: {duration})")
    
    # Add photos to albums
    if create_sub_albums:
      
        # Create sub-albums for each cluster
        for i, cluster in enumerate(clusters):
            cluster_start = min(p.date for p in cluster)
            sub_album_name = f"Cluster {i+1} ({cluster_start.strftime('%Y-%m-%d %H:%M:%S')})"

            # Create full path for nested album
            nested_album_path = f"{album}/{sub_album_name}"

            sub_album = PhotosAlbum(nested_album_path, split_folder="/")
            
            # Add photos to sub-album
            sub_album.extend(cluster)
            verbose(f"Added {len(cluster)} photos to album '{sub_album_name}'")
        
    else:
        # Add all photos to a single album
        all_photos = [photo for cluster in clusters for photo in cluster]
        album_obj = PhotosAlbum(album)
        album_obj.extend(all_photos)
        verbose(f"Added {len(all_photos)} photos to album '{album}'")
    
    # Print summary
    total_photos = sum(len(cluster) for cluster in clusters)
    click.echo(f"Found {len(clusters)} clusters with a total of {total_photos} photos")
    click.echo(f"Added photos to album '{album}'")


if __name__ == "__main__":
    main()
