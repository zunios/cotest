@echo off
python -c "from process_image import process_image; process_image('testimage.webp').save('output.png', format='PNG')"
