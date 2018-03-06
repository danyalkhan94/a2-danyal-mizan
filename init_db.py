import os
import csv
import time
import random

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
    
                                    
