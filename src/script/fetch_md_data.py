import requests, zipfile
import os
from io import BytesIO
from datetime import datetime
import calendar

now = datetime.now()

cur_month, cur_year = now.strftime('%B'), now.year
prev_month, prev_year = (calendar.month_name[now.month - 1], cur_year) \
    if now.month != 1 \
    else (calendar.month_name[12], cur_year - 1)

prefix_data_urls = {
    'CANADA': f'https://www.stevanovic.uqam.ca/LCDMA_',
    'US': f'https://files.stlouisfed.org/files/htdocs/fred-md/monthly/current.csv',
    'UK': f'https://www.stevanovic.uqam.ca/UKMD_'
}

country_reformat_exclude = ['US']


# fetch and extract the most recent monthly data from national macroeconomic databases
def download_zip_data():
    for country, url in prefix_data_urls.items():
        # fetch last month's data if current month's is unavailable
        data_url = f'{url}{cur_month}_{cur_year}.zip' if country not in country_reformat_exclude else f'{url}'
        response = requests.get(url=data_url)
        data_url = data_url if response.status_code == 200 else f'{url}{prev_month}_{prev_year}.zip'

        print(f'Downloading {country} data: {data_url}')
        response = requests.get(url=data_url)
        print(f'Download Completed')

        # extract data folder only
        folder_name = data_url.split('/')[-1].split('.')[0]
        target_dir = '../../data'
        # extract data to COUNTRY_MD folders
        if country in country_reformat_exclude:
            if not os.path.exists(f'{target_dir}/{country}_MD'):
                os.makedirs(f'{target_dir}/{country}_MD', exist_ok=True)

            with open(f'{target_dir}/{country}_MD/{country}_MD.csv', 'wb') as f:
                f.write(response.content)
        else:
            zipped_files = zipfile.ZipFile(BytesIO(response.content))
            print(f'Extracting folder {folder_name}...')
            for file in zipped_files.namelist():
                if file.startswith(folder_name):
                    zipped_files.extract(file, f'{target_dir}/{country}_MD')
                    # unify file names to lower case
                    file_name = file.split('/')[-1]
                    old_file_path = f'{os.getcwd()}/{target_dir}/{country}_MD/{folder_name}/{file_name}'
                    new_file_path = f'{os.getcwd()}/{target_dir}/{country}_MD/{folder_name}/{file_name.lower()}'
                    if file_name:
                        os.rename(src=old_file_path, dst=new_file_path)
            print(f'Extraction Completed...')

        print('##########################################################')


if __name__ == '__main__':
    download_zip_data()
