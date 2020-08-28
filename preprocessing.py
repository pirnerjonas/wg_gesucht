# encoding=utf8

import pandas as pd
import os
from geopy.geocoders import Nominatim

BASE_DIR = ''
DATA_DIR  = os.path.join(BASE_DIR, 'data/')

# create geolocator
geolocator = Nominatim(user_agent='wg_gesucht')

def load_and_append():
    current_df = pd.read_csv(os.path.join(DATA_DIR, 'current.csv'))
    # if archive exists combine currently crawled data with it
    if os.path.isfile(os.path.join(DATA_DIR, 'archive.csv')):
        archive_df = pd.read_csv(os.path.join(DATA_DIR, 'archive.csv'))
        # save raw archive
        archive_df.to_csv(os.path.join(DATA_DIR, 'archive.csv'), index=False)
        # merge old and new
        apartment_df = pd.merge(archive_df, current_df, how='outer', indicator=True)
        # make it clear where the data comes from
        apartment_df['_merge'] = apartment_df['_merge'].str.replace('left_only', 'historic')
        apartment_df['_merge'] = apartment_df['_merge'].str.replace('right_only', 'new')
        apartment_df['_merge'] = apartment_df['_merge'].str.replace('both', 'current')
        print(apartment_df['_merge'].value_counts())
        print('='*80)
        print('successfully appended data to the archive')
        print('='*80)
        return apartment_df

    # there were no prior crawls, so creat archive from the first crawl
    else:
       current_df.to_csv(os.path.join(DATA_DIR, 'archive.csv'), index=False)
       return current_df
       print('successfully created archive')

def preprocessing(apartment_df):
    # split undertitle in wg_size, location and address
    apartment_df['undertitle'] = apartment_df['undertitle'].apply(lambda x: x.split("|"))
    apartment_df['wg_size'] = apartment_df['undertitle'].str[0]
    apartment_df['location'] = apartment_df['undertitle'].str[1]
    apartment_df['address'] = apartment_df['undertitle'].str[2]

    # clean and convert price and squaremeter column
    apartment_df['price'] = apartment_df['price'].str.replace(' €','')
    apartment_df['price'] = apartment_df['price'].astype(int)
    apartment_df['squaremeter'] = apartment_df['squaremeter'].str.replace(' m²','')
    apartment_df['squaremeter'] = apartment_df['squaremeter'].astype(int)

    # helper function to retrieve geopy data
    def get_geodata(adress):
        geo_data = geolocator.geocode(adress)
        # if information has been found
        if geo_data:
            name = geo_data.raw['display_name']
            lat = float(geo_data.raw['lon'])
            lon = float(geo_data.raw['lat'])
            imp = float(geo_data.raw['importance'])

            return [name, lat, lon, imp]

    # apply helper function to location and address 
    apartment_df['geopy_info'] = apartment_df.apply(lambda x: get_geodata(x['location'] + ', ' +
                                                                          x['address']), axis=1)
    apartment_df['display_name'] = apartment_df['geopy_info'].str[0]
    apartment_df['lon'] = apartment_df['geopy_info'].str[1]
    apartment_df['lat'] = apartment_df['geopy_info'].str[2]
    apartment_df['importance'] = apartment_df['geopy_info'].str[3]

    return apartment_df

def main():
    # load the data
    print('load and append dataset')
    print('='*80)
    apartment_df = load_and_append()
    # preprocessing, split columns etc
    print('preprocess dataset')
    print('='*80)
    apartment_df = preprocessing(apartment_df)
    print('save final preprocessed data')
    print('='*80)
    apartment_df.to_csv(os.path.join(DATA_DIR, 'apartment.csv'), index=False)

if __name__ == '__main__':
    main()
