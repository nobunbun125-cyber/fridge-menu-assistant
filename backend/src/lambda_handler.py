"""AWS Lambda用エントリポイント。API GatewayからのイベントをASGIに変換する。"""

from mangum import Mangum

from src.main import app

handler = Mangum(app)
