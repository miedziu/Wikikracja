#!/bin/bash

echo; echo FIXTURES

read -r -n 1 -p "Import votings? [y/N] " answer
if [[ $answer =~ ^[Yy]$ ]]; then
  if ! sqlite3 /var/www/${APP_NAME}/db/db.sqlite3 "SELECT COUNT(*) FROM glosowania_decyzja;" | grep -q '[1-9]'; then
    /var/www/venv/bin/python /var/www/${APP_NAME}/manage.py loaddata glosowania/fixtures/votings.json
    echo "Done"
  else
    echo "No database"
  fi
else
  echo "Not imported"
fi

./manage.py loaddata glosowania/fixtures/votings.json
./manage.py loaddata chat/fixtures/chat_room.json
./manage.py loaddata board/fixtures/board.json
