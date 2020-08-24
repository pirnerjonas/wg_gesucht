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


