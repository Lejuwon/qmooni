from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.database_url)  # ✅ .env에서 불러온 값을 사용

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())  # 1 출력되면 연결 성공
    
    
# from sqlalchemy import create_engine, text

# # .env 사용 안 하고 직접 문자열로 입력
# engine = create_engine("postgresql://postgres:0000@localhost:5432/qmooni")

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT 1"))
#     print(result.scalar())