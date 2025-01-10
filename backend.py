import pandas as pd
import redis
import atexit
import json
from datetime import datetime
from celery import Celery
import subprocess
import multiprocessing


r = redis.Redis(host='localhost', port=6379, db=0)

celery = Celery('backend', broker='redis://localhost:6379/0')
def start_celery_worker():
    subprocess.Popen(["celery", "-A", "backend", "worker", "--beat", "--loglevel=info"])

csv_file = 'data.csv'
df = pd.read_csv(csv_file)

class ProductSale:
    def __init__(self, name, main_category, sub_category, image, link, ratings, no_of_ratings, actual_price, discount_price, sale_dates={}):
        self.name = name
        self.main_category = main_category
        self.sub_category = sub_category
        self.image = image
        self.link = link
        self.ratings = ratings
        self.no_of_ratings = no_of_ratings
        self.actual_price = actual_price
        self.discount_price = discount_price
        self.sale_dates = sale_dates
    
    def to_dict(self):
        return {
            'name': self.name,
            'main_category': self.main_category,
            'sub_category': self.sub_category,
            'image': self.image,
            'link': self.link,
            'ratings': self.ratings,
            'no_of_ratings': self.no_of_ratings,
            'actual_price': self.actual_price,
            'discount_price': self.discount_price,
            'sale_dates': self.sale_dates,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            main_category=data['main_category'],
            sub_category=data['sub_category'],
            image=data['image'],
            link=data['link'],
            ratings=data['ratings'],
            no_of_ratings=data['no_of_ratings'],
            actual_price=data['actual_price'],
            discount_price=data['discount_price'],
            sale_dates=data['sale_dates'],
        )
    
    def save(self, key):
        r.set(key, json.dumps(self.to_dict()))

    @classmethod
    def load(cls, key):
        data = r.get(key)
        if data:
            data = json.loads(data)
            # normalize date format 
            data['sale_dates'] = {
                datetime.strptime(key,'%m/%d/%Y').date().strftime('%m/%d/%Y'): value
                for key, value in data['sale_dates'].items()
            }
            return cls.from_dict(data)
        else:
            return None


class DatesList:
    def __init__(self, redis_key):
        self.redis_key = redis_key

    def __getitem__(self, index):
        date_str = r.lindex(self.redis_key, index).decode('utf-8')
        return datetime.strptime(date_str,'%m/%d/%Y').date()
    
    def get_all_dates(self):
        return [self[i] for i in range(len(self))]

    def __len__(self):
        return r.llen(self.redis_key)
    

class ProductsList:
    def __init__(self, redis_key='names'):
        self.redis_key = redis_key
        # flush redis for all before exiting 
        atexit.register(self.cleanup)

    def __getitem__(self, index):
        product_name = r.lindex(self.redis_key, index)
        return product_name.decode() if product_name else None

    def __len__(self):
        return r.llen(self.redis_key)

    def add_products(self, product_names):
        r.rpush(self.redis_key, *product_names)

    def get_all_products(self):
        return [self[i] for i in range(len(self))]
    
    def cleanup(self):
        r.flushdb()

@celery.task
def set_products_list():
    if not r.exists('names'):
        product_list = ProductsList()
        product_names = df['name'].unique().tolist()
        product_list.add_products(product_names)

@celery.task
def set_dates_list():
    if not r.exists('dates'):
        dates = df['date'].unique()
        r.rpush('dates', *dates)

@celery.task
def set_porduct_sale_list():
    unique_names = df['name'].unique()
    unique_dates = df['date'].unique()
    for name in unique_names:
        # get the first row of the product sale to set generic attrs
        fps = df.loc[df['name'] == name].iloc[0]
        ps = ProductSale(name=name, 
                         main_category=fps['main_category'],
                         sub_category=fps['sub_category'],
                         image=fps['image'],
                         link=fps['link'],
                         ratings=fps['ratings'],
                         no_of_ratings=fps['no_of_ratings'],
                         actual_price=fps['actual_price'],
                         discount_price=fps['discount_price'],
                         )
        # calculate sale count of the product based on dates
        ps.sale_dates = {date: 0 for date in unique_dates}
        ps.sale_dates.update(df.loc[df['name'] == name]['date'].value_counts().to_dict())
        ps.save(name)