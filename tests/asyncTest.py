# %%
from time import sleep
import asyncio

async def asyncFunction(n:int, s:int):
    await print(f'function{n} start')
    asyncio.sleep(s)
    await print(f'function{n} end')

# %%
def standerdFunction(n:int, s:int):
    print(f'standerd function {n} start')
    sleep(s)
    print(f'starderd function {n} end')

# %%
asyncFunction(1, 3)
standerdFunction(1, 3)
asyncFunction(2, 3)



