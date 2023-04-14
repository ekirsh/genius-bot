STORAGE_DIR=/opt/render/project/.render
export CHROME_PATH="$STORAGE_DIR/chrome/opt/google/chrome/google-chrome"
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

gunicorn app:app