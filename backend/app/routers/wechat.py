from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import httpx
import os

from ..database import get_db
from ..models import User
from ..auth import create_access_token

router = APIRouter(prefix="/auth/wechat", tags=["auth"])

# 微信开放平台配置
# 请替换为你自己的微信开放平台 AppID 和 AppSecret
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "YOUR_WECHAT_APP_ID")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "YOUR_WECHAT_APP_SECRET")


class WeChatCodeRequest(BaseModel):
    code: str


class WeChatLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


async def get_wechat_openid(code: str) -> dict:
    """通过 code 获取微信用户的 openid"""
    async with httpx.AsyncClient() as client:
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": WECHAT_APP_ID,
            "secret": WECHAT_APP_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
        response = await client.get(url, params=params)
        return response.json()


async def get_wechat_userinfo(openid: str, access_token: str) -> dict:
    """获取微信用户信息"""
    async with httpx.AsyncClient() as client:
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid
        }
        response = await client.get(url, params=params)
        return response.json()


@router.post("/login", response_model=WeChatLoginResponse)
async def wechat_login(request: WeChatCodeRequest, db=Depends(get_db)):
    """
    微信登录
    
    移动端流程:
    1. 调用微信 SDK 获取 code
    2. 将 code 发送到本接口
    3. 后台通过 code 换取 openid 和 access_token
    4. 通过 openid 查找或创建用户
    5. 返回 JWT token
    
    前端示例:
    ```javascript
    // 微信 SDK 登录
    WXApi.sendReq(new SendAuth.Req({
      scope: 'snsapi_userinfo',
      state: 'wechat_login'
    }))
    
    // 微信回调后，调用本接口
    const res = await fetch('/api/auth/wechat/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: '微信返回的code' })
    })
    ```
    """
    try:
        # 换取 openid 和 access_token
        token_data = await get_wechat_openid(request.code)
        
        if "errcode" in token_data and token_data["errcode"] != 0:
            raise HTTPException(
                status_code=400,
                detail=f"微信登录失败: {token_data.get('errmsg', '未知错误')}"
            )
        
        openid = token_data.get("openid")
        wechat_access_token = token_data.get("access_token")
        
        if not openid:
            raise HTTPException(status_code=400, detail="无法获取微信 openid")
        
        # 查找或创建用户
        from sqlalchemy.orm import Session
        db: Session = next(get_db())
        
        user = db.query(User).filter(User.wechat_openid == openid).first()
        
        if not user:
            # 获取微信用户信息
            try:
                wechat_user = await get_wechat_userinfo(openid, wechat_access_token)
                nickname = wechat_user.get("nickname", f"用户_{openid[:8]}")
                avatar = wechat_user.get("headimgurl")
            except:
                nickname = f"用户_{openid[:8]}"
                avatar = None
            
            # 创建新用户
            user = User(
                username=nickname,
                phone=f"wechat_{openid[:8]}",  # 临时手机号格式
                password_hash="",  # 微信登录不需要密码
                avatar=avatar,
                wechat_openid=openid,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 创建 JWT token
        access_token_jwt = create_access_token(data={"sub": str(user.id)})
        
        return WeChatLoginResponse(
            access_token=access_token_jwt,
            user={
                "id": user.id,
                "name": user.username,
                "phone": user.phone,
                "avatar": user.avatar,
                "rating": 5.0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 如果是演示模式（没有配置真实的微信 AppID），返回模拟数据
        if WECHAT_APP_ID == "YOUR_WECHAT_APP_ID":
            # 演示模式：创建模拟用户
            demo_user = {
                "id": 999,
                "name": "微信用户",
                "phone": "wechat_demo",
                "avatar": None,
                "rating": 5.0
            }
            demo_token = create_access_token(data={"sub": "999"})
            return WeChatLoginResponse(
                access_token=demo_token,
                user=demo_user
            )
        
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/qrcode")
async def get_wechat_qrcode_url():
    """
    获取微信授权码 URL（用于网页端扫码登录）
    
    返回示例:
    {
      "url": "https://open.weixin.qq.com/connect/qrconnect?..."
    }
    """
    redirect_uri = os.getenv("WECHAT_REDIRECT_URI", "http://localhost:8000/api/auth/wechat/callback")
    url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={WECHAT_APP_ID}"
        f"&redirect_uri={httpx.URL(redirect_uri).encode().decode()}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state=wechat_login"
    )
    return {"url": url}
