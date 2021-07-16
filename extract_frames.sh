ffmpeg -skip_frame nokey -i mow_cut.mp4 -vsync 0 -r 30 -f image2 thumbnails-%05d.jpg
