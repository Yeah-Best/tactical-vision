"""测试腾讯元器智能体连接"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.hunyuan_client import hunyuan_client

async def test_yuanqi_connection():
    """测试腾讯元器智能体连接"""
    print("开始测试腾讯元器智能体连接...")
    print("=" * 50)
    
    # 测试基本对话功能
    messages = [
        {
            "role": "user",
            "content": "你好，请介绍一下你自己"
        }
    ]
    
    try:
        print("\n发送测试消息...")
        response = await hunyuan_client.chat_completions(messages)
        
        print("\n智能体回复:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        print("\n腾讯元器智能体连接成功！")
        return True

    except Exception as e:
        print(f"\n连接失败: {str(e)}")
        print("\n请检查:")
        print("1. .env 文件中的 YUANQI_API_KEY 和 YUANQI_AGENT_ID 是否正确")
        print("2. 网络连接是否正常")
        print("3. 腾讯元器服务是否可用")
        return False

async def test_streaming():
    """测试流式对话"""
    print("\n" + "=" * 50)
    print("测试流式对话功能...")
    print("=" * 50)
    
    messages = [
        {
            "role": "user", 
            "content": "请用3句话介绍一下王者荣耀的基本玩法"
        }
    ]
    
    try:
        print("\n流式回复:")
        print("-" * 50)
        
        async for chunk in hunyuan_client.chat_completions_stream(messages):
            print(chunk, end="", flush=True)
            
        print("\n" + "-" * 50)
        print("\n流式对话功能正常！")
        return True

    except Exception as e:
        print(f"\n流式对话失败: {str(e)}")
        return False

async def test_emotion_analysis():
    """测试情绪分析"""
    print("\n" + "=" * 50)
    print("测试情绪分析功能...")
    print("=" * 50)
    
    user_message = "今天又输了，真的很郁闷"
    
    try:
        print("\n情绪分析:")
        print("-" * 50)
        
        async for chunk in hunyuan_client.analyze_emotion(
            user_message=user_message,
            emotion_type="自责",
            emotion_level=7
        ):
            print(chunk, end="", flush=True)
            
        print("\n" + "-" * 50)
        print("\n情绪分析功能正常！")
        return True

    except Exception as e:
        print(f"\n情绪分析失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("  腾讯元器智能体连接测试")
    print("=" * 50)
    
    # 测试基本对话
    test1 = await test_yuanqi_connection()
    
    # 测试流式对话
    test2 = await test_streaming()
    
    # 测试情绪分析
    test3 = await test_emotion_analysis()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"基本对话: {'[通过]' if test1 else '[失败]'}")
    print(f"流式对话: {'[通过]' if test2 else '[失败]'}")
    print(f"情绪分析: {'[通过]' if test3 else '[失败]'}")
    print("=" * 50)
    
    if test1 and test2 and test3:
        print("\n所有测试通过！腾讯元器智能体已成功连接并可以正常使用。")
        return 0
    else:
        print("\n部分测试失败，请检查配置和服务状态。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)