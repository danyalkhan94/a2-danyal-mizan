

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class User(db.Model, UserMixin):
    __tablename__ = 'users'

   
        post.modified  = datetime.now()
        db.session.add(post)
        db.session.commit()    
        return redirect(url_for('dashboard'))