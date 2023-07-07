import sqlite3



def store_challenge(challenge_string: str):
        try:
                dbconnect = sqlite3.connect(authbot_path + "authbot")
                cursor = dbconnect.cursor()
                sql = "INSERT INTO challenge(challenge_string) VALUES('" + challenge_string + "')"
                print(sql)
                count = cursor.execute(sql)
                dbconnect.commit()
                cursor.close()
                return True
        except sqlite3.Error as error:
                print("Failed to insert record into the database.", error)
                return False
#        finally:
#                if dbconnect:
#                        dbconnect.close()
#                        print("Database connection closed.")
#                        return False


authbot_path = '/home/user/authbot/'
retval = store_challenge('bbdbd6db-de91-4fee-b9dc-9fcfa118f03d')

print(retval)

