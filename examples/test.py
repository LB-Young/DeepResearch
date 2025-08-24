import asyncio
import time

class A:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    async def change_age(self, new_age):
        await asyncio.sleep(3)
        self.age = new_age
        asyncio.create_task(self.change_name("b"))

    async def change_name(self, new_name):
        await asyncio.sleep(3)
        self.name = new_name

    async def get_age(self):
        return self.age

    async def get_name(self):
        return self.name

p_1 = A("a", 1)
list_a = [p_1]

async def main():
    # 启动属性修改任务
    asyncio.create_task(p_1.change_age(2))

    
    while True:
        
        age = await p_1.get_age()
        name = await p_1.get_name()
        print(f"Name: {name}, Age: {age}")
        await asyncio.sleep(1)

asyncio.run(main())