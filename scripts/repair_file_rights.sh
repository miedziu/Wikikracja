#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Usage: $(basename $0) folder user group"
  echo "  folder: Folder in which rights should be changed"
  echo "  user: owner"
  echo "  group: group"
  echo "  e.g: /file_rights.sh . wiki www-data <- means current folder"
  exit 1
fi

chown -R $2:$3 $1

find $1 -type f -exec chmod 640 {} \;
find $1 -type d -exec chmod 750 {} \;

chmod 500 $1/manage.py
chmod 700 $1/scripts/*.sh
# chmod 660 $1/db/db.sqlite3

# ls -alh
echo ""
