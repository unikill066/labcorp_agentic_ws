from crew_config import build_crew
import sys, asyncio

if __name__ == "__main__":
    keyword = " ".join(sys.argv[1:]) or input("Keyword: ")
    asyncio.run(build_crew(keyword).run())
