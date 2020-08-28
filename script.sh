# connect to nordvpn
nordvpn connect 

# remove the last current file
FILE=./data/current.csv
if [ -f "$FILE" ]; then
   rm $FILE
   echo "sucessfully removed last current file"
fi

# start crawling
cd scrapy_project/
scrapy crawl wg_spider -o ../data/current.csv
cd ..

# start preprocessing
python preprocessing.py

git add .
git commit -m "push data from automatic run"
git push

git push heroku-staging master

heroku ps:scale web=1 
