import os
import csv
import time
import random
from datetime import datetime, timedelta


from blogspace import app, db, User, Post


def gen_link(string, date, maxlen):
    '''
    creates an url identifier from given string and date objects
    '''
    p = date.strftime("%s")
    t = '-'.join(string.split())
    u = ''.join([c for c in t if c.isalnum() or c == '-'])   # remove punctation   
    strlen = maxlen - len(p) - 1
    return u[:strlen].rstrip('-').lower() + '-' + p 




   

def init_db():

    sample_data_dir = os.path.join(app.config['APP_DIR'], 'data', 'sample-data')

    with app.app_context():
        
        db.drop_all()
        db.create_all()
        
        # create sample users
        users_fname = os.path.join(sample_data_dir, 'users.txt')
        with open(users_fname, 'r') as fp: 
            reader = csv.DictReader(fp)
            users  = list(reader)

        for i, item in enumerate(users):
            fname, lname = item['full_name'].split() 
            email  = item['email']
            passwd = fname.lower() + lname.lower()
            
            user = User(fname, lname, email, passwd)
            
            user.logo = app.config['DEFAULT_USER_LOGO'] #item['image_url']
            user.occupation = item['job']
            user.bio = item['bio']
            user.confirmed = True

            db.session.add(user)
        
        # create sample posts
        categories = ['abstract', 'animals', 'business', 'cats', 'city', 
                      'food', 'nightlife', 'fashion', 'people', 'nature', 
                      'sports', 'technics', 'transport']
            
        titles_fname = os.path.join(sample_data_dir, 'titles.txt')
        with open(titles_fname, 'r') as fp:
            titles = fp.read().splitlines()
        
        fname = os.path.join(sample_data_dir, 'lorem_ipsum.txt')
        with open(fname) as fp:
            post_text = fp.read()
        nposts = 100
        for i in range(nposts):
        
            category = random.choice(categories)
            title = random.choice(titles)
            
            post = Post(title, post_text, category)
            post.userid = random.randint(1, len(users))
            post.image_url = 'http://lorempixel.com/850/400/' + category + '/' + str(i % 10 + 1)
            post.modified  = datetime.now() - timedelta(minutes=i)
            post.views = random.randint(400, 1000)
            post.likes = random.randint(50, 350)
            
            db.session.add(post)

        db.session.commit()
                        
                                
if __name__ == '__main__':
    init_db()
    
                                    
