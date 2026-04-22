"""测试腾讯元器网络连接"""
import asyncio
import httpx

async def test_yuanqi_network():
    """测试腾讯元器API网络连接"""
    print("测试腾讯元器API网络连接...")
    
    url = "https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions"
    headers = {
        "X-source": "openapi",
        "Content-Type": "application/json",
        "Authorization": "Bearer utXTbDpy1sCgupaMfCVN7PhBkQfDRgL1"
    }
    
    # 测试GET请求
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            print(f"请求URL: {url}")
            resp = await client.get(url, headers=headers)
            print(f"状态码: {resp.status_code}")
            print(f"响应内容: {resp.text[:500]}")
            
            if resp.status_code == 405:
                print("\n注意: 状态码405表示方法不允许，需要使用POST请求")
                
    except Exception as e:
        print(f"网络连接失败: {str(e)}")
    
    # 测试POST请求
    try:
        payload = {
            "assistant_id": "2038933396066927680",
            "user_id": "test_user",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "你好"
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            print("\n测试POST请求...")
            resp = await client.post(url, headers=headers, json=payload)
            print(f"状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                print("腾讯元器API连接成功！")
                print(f"响应: {resp.text[:500]}")
                return True
            else:
                print(f"腾讯元器API返回错误状态码: {resp.status_code}")
                print(f"响应: {resp.text}")
                return False
                
    except Exception as e:
        print(f"POST请求失败: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_yuanqi_network())
    if result:
        print("\n腾讯元器智能体网络连接测试通过")
    else:
        print("\n腾讯元器智能体网络连接测试失败")