from app.agent.function_agent import run_function_agent

RAG_TEST_CASES = [
    "公司的保密制度是什么？",
    "差旅报销标准是多少？",
    "员工年假有多少天？",
    "公司的考勤制度是什么？",
    "请帮我统计一下知识库有多少条向量",
]

def test_agent_interactive():
    print("=" * 60)
    print("🤖 Agent RAG 工具测试（交互式）")
    print("=" * 60)
    print("输入问题测试，输入 q 退出")
    
    while True:
        question = input("\n请输入你的问题：")
        if question.strip().lower() == "q":
            print("👋 退出测试")
            break
        if not question.strip():
            continue
        
        print("\n🤖 Agent 正在思考...")
        try:
            result = run_function_agent(question)
            print(f"\n🔍 思考过程：")
            for step in result["steps"]:
                print(step)
            print(f"\n📝 回答：{result['answer']}")
        except Exception as e:
            import traceback
            print(f"\n❌ 错误：{e}")
            traceback.print_exc()

def test_agent_auto():
    print("=" * 60)
    print("🤖 Agent RAG 工具自动测试")
    print("=" * 60)
    
    for question in RAG_TEST_CASES:
        print(f"\n📌 问题：{question}")
        print("-" * 40)
        try:
            result = run_function_agent(question)
            print(f"\n🔍 思考过程：")
            for step in result["steps"]:
                print(step)
            print(f"\n📝 回答：{result['answer']}")
        except Exception as e:
            import traceback
            print(f"\n❌ 错误：{e}")
            traceback.print_exc()
        print()

if __name__ == "__main__":
    print("请选择测试模式：")
    print("1. 交互式测试（手动输入问题）")
    print("2. 自动测试（预设 RAG 用例）")
    
    choice = input("\n请输入选项（1/2）：")
    
    if choice == "1":
        test_agent_interactive()
    elif choice == "2":
        test_agent_auto()
    else:
        print("无效选项")