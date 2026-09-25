import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import auth, history, ingredients, menu
from src.core.config import settings
from src.db.session import engine
from src.models import Base

logger = logging.getLogger("app")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="冷蔵庫AI献立アシスタント API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # FastAPIの標準エラーレスポンスはCORSMiddlewareを経由せず返されることがあり、
    # ブラウザ側では実際のエラー内容が見えない「CORSエラー」に化けてしまう。
    # ここで自前のJSONResponseを返すことで、必ずCORSヘッダー付きでフロントに届くようにする。
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "サーバー内部でエラーが発生しました。しばらくしてから再度お試しください。"},
    )


app.include_router(auth.router)
app.include_router(ingredients.router)
app.include_router(menu.router)
app.include_router(history.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
