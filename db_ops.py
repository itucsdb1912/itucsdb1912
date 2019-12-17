import psycopg2 
from urllib.parse import urlparse
from SQL_QUERIES import SQL_QUERIES

class database:
    def __init__(self):
        self.connection = None
        self.url = urlparse("postgres://padrjufxoslazm:66097f7c6a273316c865544b566106405e2d014e3f6f61ea3de5d71d42668c0c@ec2-54-247-178-166.eu-west-1.compute.amazonaws.com:5432/d65tnih23lgdao")
    #INITIALIZING DB 
    def connect_db(self):
        try:
            self.connection = psycopg2.connect(database = self.url.path[1:],
                                                user = self.url.username,
                                                password = self.url.password,
                                                host = self.url.hostname)
            print("Connected!")
            return self.connection
        except:
            print("Connection Failed")
            return False
    def create_tables(self):
        table_list = ['create_user_table', 'create_store_table', 'create_product_table', 'create_variant_table']
        for create in table_list:
            with self.connection.cursor() as cursor:
                sql = SQL_QUERIES[create]
                cursor.execute(sql,)
            self.connection.commit()
        print("Tables ready.")
        return {"err": None, "msg": "Tables are ready to use."}

    def create_user(self, username, email, password):  
        try:    
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = SQL_QUERIES['create_user']
                cursor.execute(sql, (username, email, password))
                result = cursor.fetchone()
                print(result)
            self.connection.commit()
            print("You have successfully signed up.")
            return {"err": None, "msg": "You have successfully signed up."," user": {"id": result[0], "username": result[1]}}
        except:
            self.connection.rollback()
            print("Username or email has taken")
            return {"err": "Username or email has taken"}     
    def check_user(self, username, password):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id, Username, Password FROM Account WHERE Username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()

        if result == None:
            print("User not found.")
            return {'err': 'User not found.' }
        else:
            if result[2] == password:
                print("Login successful.")
                return {'err': None, 'msg': 'Login successful.', 'user': {"id":result[0],"username": result[1]}}
            else:
                print("Wrong password.")
                return {'err': 'Wrong password.'}
    def new_store(self, userid, name, address, apikey='default', password='default'):
        with self.connection.cursor() as cursor:
            try:
                # Create a new record
                sql = SQL_QUERIES['new_store']
                cursor.execute(sql, (name, address, userid, apikey, password))
                self.connection.commit()
                print("You have successfully opened a store.")
                return {'err': None, 'msg': 'Store is opened.'}
            except:
                self.connection.rollback()
                print("This store name exists. Please pick another name.")
                return {'err': 'Store name exists.'}            
    def add_product(self, storeid, product):
        # insert to variants with saved product_id
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = SQL_QUERIES['add_product']
                cursor.execute(sql, (product['id'],
                                    product['title'],
                                    product['price'],
                                    product['description'],
                                    product['store_id'],))

            self.connection.commit()
            for variant in product['variants']:
                db.add_variant(variant)
            print("You have successfully created a product.")
            return {'err':None,'msg':'You have successfully created a product.'}
        except:
            self.connection.rollback()
            print("This product exists.")
            return {'err':'This product exists.'}
    def add_variant(self, variant):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = SQL_QUERIES['add_variant']
            cursor.execute(sql, (variant['id'], 
                                variant['option1'], 
                                variant['option2'], 
                                variant['option3'], 
                                variant['stock'],
                                variant['sku'],
                                variant['compare_at_price'],
                                variant['product_id'],))
        self.connection.commit()
        print("You have successfully added a variant.")
        return {'err':None,'msg':'You have successfully added a variant.'}

    def update_user(self, id, username, email):
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE Account SET Username =%s WHERE Id=%s"
                cursor.execute(sql, (username, id,))
                self.connection.commit()
                print("Username changed.")
                return {'err': None, 'msg': 'Username changed.'}
        except:
            self.connection.rollback()
            print("Username already exists.")
            return {'err': 'Username already exists.'}
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE Account SET Email =%s WHERE Id=%s"
                cursor.execute(sql, (email, id,))
                self.connection.commit()
                print("Email changed.")
                return {'err': None, 'msg': 'Email changed.'}
        except:
            self.connection.rollback()
            print("Email already exists.")
            return {'err': 'Email already exists.'}
    def change_password(self, id, oldpassword, newpassword):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Password FROM Account WHERE Id=%s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
        if result != None and result[0] == oldpassword:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE Account SET Password=%s WHERE Id=%s"
                cursor.execute(sql, (newpassword,id))
            self.connection.commit()
            print("Password successfully updated.")
            return {'err': None, 'msg': 'Password successfully updated.'}
        elif result == None:
            print("User does not exist.")
            return {'err': 'User does not exist.'}
        else:
            print("Password does not match.")
            return {'err': 'Password does not match.'}
    def update_store(self, id, name, address, apikey, password):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM Store WHERE Id=%s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            sql = "SELECT Id FROM Store WHERE StoreName=%s"
            cursor.execute(sql, (name,))
            nameexists = cursor.fetchone()
        if result != None:
            if nameexists == None:
                with self.connection.cursor() as cursor:
                    # Create a new record
                    sql = "UPDATE Store SET Address=%s, StoreName=%s, ApiKey=%s, Password=%s WHERE Id=%s"
                    cursor.execute(sql, (address, name, apikey, password, id,))
                self.connection.commit()
                print("Store successfully updated.")
                return {'err': None, 'msg': 'Store successfully updated.'}
            else:
                print("Store name already exists")
                return {'err': 'Store name already exists.'}
            
        else:
            print("Store does not exist.")
            return {'err': 'Store does not exist.'}
    def update_product(self, product):
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE Product \
                    SET ProductName=%s, ProductPrice=%s,ProductDescription=%s,StoreId=%s,WHERE Id=%s"
                cursor.execute(sql, (product['title'], 
                                    product['price'], 
                                    product['description'], 
                                    product['store_id'], 
                                    product['id']))
                self.connection.commit()
                print("Product attributes changed.")
                return {'err': None, 'msg': 'Product attributes changed.'}
        except:
            self.connection.rollback()
            print("Username already exists.")
            return {'err': 'Username already exists.'}

    def change_productprice(self, id, newprice):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM ProductInfo WHERE Id=%s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE ProductInfo SET ProductPrice=%s WHERE Id=%s"
                cursor.execute(sql, (newprice,id))
            self.connection.commit()
            print("Product price successfully updated.")
            return True
        else:
            print("Entered product cannot be found.")
            return False
    def change_productdiscount(self, id, newdiscount):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM ProductInfo WHERE Id=%s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE ProductInfo SET ProductDiscount=%s WHERE Id=%s"
                cursor.execute(sql, (newdiscount,id))
            self.connection.commit()
            print("Product discount successfully updated.")
            return True
        else:
            print("Entered product cannot be found.")
            return False
    def update_variantstock(self, id, newstock):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM ProductVariantInfo WHERE Id=%s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE ProductVariantInfo SET Stock=%s WHERE Id=%s"
                cursor.execute(sql, (newstock, id))
            self.connection.commit()
            print("Variant stock successfully updated.")
            return True
        else:
            print("Entered variant cannot be found.")
            return False

    def get_product(self, id=None):
        if id != None:
            sql = "SELECT * FROM Product WHERE Id=%s"
            with self.connection.cursor() as cursor:
                cursor.execute(sql,(id,))
                result = cursor.fetchone()
            if result != None:
                return {'err':None, 'msg': 'One Product data collected.', 'data':{'id':result[0], 
                                                                        'title':result[1], 
                                                                        'price':result[2],
                                                                        'description':result[3],
                                                                        'timestamp':result[4],
                                                                        'storeid':result[5]}}
            else:
                return {'err':'Id cannot be found.'}
                
        else:
            sql = "SELECT * FROM Product"
            with self.connection.cursor() as cursor:
                cursor.execute(sql,())
                result = cursor.fetchall()
            message = {'err':None, 'msg': 'All Product data collected.', 'data': []}
            for product in result:
                message['data'].append({'id':product[0], 
                                        'title':product[1], 
                                        'price':product[2],
                                        'description':product[3],
                                        'timestamp':product[4],
                                        'storeid':product[5]})
            return message
    def get_store(self, id=None):
        if id != None:
            sql = "SELECT * FROM Store WHERE Id=%s"
            with self.connection.cursor() as cursor:
                cursor.execute(sql,(id,))
                result = cursor.fetchone()
            if result != None:
                return {'err':None, 'msg': 'One store data collected.', 'data':{'id':result[0], 
                                                                        'apikey':result[1], 
                                                                        'password':result[2],
                                                                        'storename':result[3],
                                                                        'address':result[4],
                                                                        'timestamp':result[5],
                                                                        'userid':result[6],
                                                                        'isactivated':result[7]}}
            else:
                return {'err':'Id cannot be found.'}
                
        else:
            sql = "SELECT * FROM Store"
            with self.connection.cursor() as cursor:
                cursor.execute(sql,())
                result = cursor.fetchall()
            message = {'err':None, 'msg': 'All store data collected.', 'data': []}
            for store in result:
                message['data'].append({'id':store[0], 
                                            'apikey':store[1], 
                                            'password':store[2],
                                            'storename':store[3],
                                            'address':store[4],
                                            'timestamp':store[5],
                                            'userid':store[6],
                                            'isactivated':store[7]})
            return message
    def get_user(self, id):
        if id != None:
            sql = "SELECT * FROM Account WHERE Id=%s"
            with self.connection.cursor() as cursor:
                cursor.execute(sql,(id,))
                result = cursor.fetchone()
            if result != None:
                return {'err':None, 'msg': 'One user data collected.', 'data':{'id':result[0], 
                                                                        'username':result[1], 
                                                                        'email':result[2],
                                                                        'timestamp':result[3],
                                                                        'password':result[4]}}
            else:
                return {'err':'Id cannot be found.'}

    def delete_account(self, userid):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM Account WHERE Id=%s"
            cursor.execute(sql, (userid,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "DELETE FROM Account WHERE Id=%s"
                cursor.execute(sql, (userid,))
            self.connection.commit()
            print("User successfully deleted.")
            return True
        else:
            print("User deletion failed.")
            return False
    def delete_store(self, storeid):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM Store WHERE Id=%s"
            cursor.execute(sql, (storeid,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "DELETE FROM Store WHERE Id=%s"
                cursor.execute(sql, (storeid,))
            self.connection.commit()
            print("Store successfully deleted.")
            return True
        else:
            print("Store deletion failed.")
            return False
    def delete_product(self, productid):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM Product WHERE Id=%s"
            cursor.execute(sql, (productid,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "DELETE FROM Product WHERE Id=%s"
                cursor.execute(sql, (productid,))
            self.connection.commit()
            print("Product successfully deleted.")
            return True
        else:
            print("Product deletion failed.")
            return False
    def delete_variant(self, variantid):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT Id FROM ProductVariant WHERE Id=%s"
            cursor.execute(sql, (variantid,))
            result = cursor.fetchone()
        if result != None:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "DELETE FROM ProductVariant WHERE Id=%s"
                cursor.execute(sql, (variantid,))
            self.connection.commit()
            print("Variant successfully deleted.")
            return True
        else:
            print("Variant deletion failed.")
            return False

    # SOME UTILITY METHODS
    def drop_tables(self):
        table_list = ['Account', 'Store', 'Product', 'ProductVariant']
        for table in table_list:
            with self.connection.cursor() as cursor:
                sql = "DROP TABLE " + table + " CASCADE"
                cursor.execute(sql,())
            self.connection.commit()
        print("Tables deleted.")
        return {"err": None, "msg": "Tables are dropped, please create again to continue."} 
    def get_data(self, tablename):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM " + tablename
            cursor.execute(sql, )
            result = cursor.fetchall()
            print(result)
    def has_user(self):
        sql_query = "SELECT Id FROM Account"
        with self.connection.cursor() as cursor:
            cursor.execute(sql_query,)
            result = cursor.fetchone()
        if result == None:
            return False
        else:
            return True
    def get_schemas(self):
        sql = "select schema_name from information_schema.schemata;"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, ())
            result = cursor.fetchall()
            print(result)
    def get_tablenames(self):
        sql = SQL_QUERIES["get_tables"]
        with self.connection.cursor() as cursor:
            cursor.execute(sql, ())
            result = cursor.fetchall()
            print(result)
    def get_colnames(self, tablename):
        sql = "SELECT COLUMNS FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (tablename,))
            result = cursor.fetchall()
            print(result)

db = database()
db.connect_db()
db.drop_tables()
#db.get_schemas()
#db.get_tablenames()
db.create_tables()
db.get_data("Account")
db.create_user("test4", "test4@test.com", "secret2")

db.update_user(1, "test4", "test5@test.com")

db.new_store(1, "teststore2", "Istanbul")
db.get_data("Account")
db.change_password(1, "secret2", "changedsecret")
db.update_store(1, "teststorechanged", "Istanbul", "agad98765", "684sag1sd32fa65")

product = {
        "id": 35468,
        "title": "Test Product",
        "price": 99.00,
        "description": "lorem ipsum",
        "store_id": 1,
        "variants": [
            {
                "id": 54634,
                "option1":"yellow",
                "option2":"L",
                "option3":"95cotton",
                "sku": "SKWE-234",
                "stock": 324,
                "compare_at_price": 88,
                "product_id": 35468,
            }
        ]
        
    }

#db.add_product(1,product)
#db.get_colnames("store")
#db.new_store(3, "teststore2", "Istanbul")



#uid = user, sid = store, pid = product, vid = variant
#You need to check uid, sid, pid and vid to ensure they get the right values as in the database table
#Thats because auto increment continues from the last value
#(e.g. new id can be 9, even if there is no 8. That means id 8 is created before but it is deleted.)

#All above functions are tested.