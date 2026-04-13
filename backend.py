from db import database
import random,threading,asyncio
from pyrogram import Client

DB = database()
api_id = '20663523'
api_hash = 'f75fe6157dd68bdf0df5198adbc590fd'
class app :
    async def ADDuser(self,GrobUser,inGRob,id,bot):
        list = DB.accounts()
        random.shuffle(list)
        numberMin = 40
        inGRob = inGRob.split("/")[3]
        for name in list :
            num = 0          
            for user in GrobUser:      
                try:
                    num +=1
                    GrobUser.remove(user)
                    async with Client("::memory::", api_id, api_hash,no_updates=True,in_memory=True,lang_code="ar",session_string=name) as app:
                        await asyncio.sleep(10)
                        try:
                            print(user)            
                            await app.add_chat_members(inGRob, user)                    
                        except Exception as e:
                            print(e)
                            if "FLOOD_WAIT_X" in str(e):
                                break
                            pass
                    if num== numberMin :
                        break
                except:
                    pass          
    async def GETuser(self,GrobUser,Ingrob):
        if 0 == 0:  
            list = DB.accounts()
            random.shuffle(list)
            GrobUser = GrobUser.split("/")[3]
            print(3)   
            Ingrob = Ingrob.split("/")[3]       
            if list and len(list) > 0:
                name = "".join(random.choice(list) for i in range(1))
            else:
                name = "User_" + str(random.randint(1000, 9999))
            administrators = []
            async with Client("::memory::", api_id, api_hash,no_updates=True,in_memory=True,lang_code="ar",session_string=name) as app:      
                await app.join_chat(Ingrob)
                # سحب الأعضاء العاديين
                async for m in app.get_chat_members(GrobUser):
                    try:
                        if m.user.username != None:
                           administrators.append(m.user.username)
                    except:
                        pass
                
                # سحب المتفاعلين لتجاوز الإخفاء (قوة إضافية)
                try:
                    active_users = await self.get_active_users(app, GrobUser)
                    for user in active_users:
                        if user.username and user.username not in administrators:
                            administrators.append(user.username)
                except Exception as e:
                    print(f"Error scraping active users: {e}")
            threading.current_thread().return_value = administrators	
            print(administrators)
            return administrators
        # except Exception as e:
        #     print(e)

       

    async def get_active_users(self, app, group_id, limit=1000):
        """سحب المتفاعلين لتجاوز خاصية الإخفاء"""
        participants = []
        seen_ids = set()
        try:
            async for message in app.get_chat_history(group_id, limit=limit):
                if message.from_user and not message.from_user.is_bot:
                    if message.from_user.id not in seen_ids:
                        participants.append(message.from_user)
                        seen_ids.add(message.from_user.id)
        except Exception as e:
            print(f"History error: {e}")
        return participants

