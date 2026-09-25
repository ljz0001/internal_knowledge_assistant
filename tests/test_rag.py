from app.rag.rag_server import (
    rag_search,
    rag_add_file,
    rag_add_files,
    rag_delete_file,
)
from app.rag.vector_store import get_vector_store
from app.config.settings import DOCS_DIR


def test_rag_search():
    """测试RAG问答"""
    question = input("请输入你的问题：")
    if not question.strip():
        print("⚠️ 问题不能为空")
        return
    print("\n🤖 正在检索并生成回答...")
    answer = rag_search(question)
    print(f"\n📝 回答：{answer}")


def test_rag_init():
    """测试全量入库"""
    vs = get_vector_store()
    before = vs._collection.count()
    print(f"当前向量库中有 {before} 条向量")

    confirm = input("是否执行全量入库？(y/n)：")
    if confirm.lower() != "y":
        print("已取消")
        return

    from app.rag.loader import load_documents_from_dir
    from app.rag.splitter import get_text_splitter
    from app.rag.vector_store import add_documents

    print(f"📂 扫描目录：{DOCS_DIR}")
    docs = load_documents_from_dir(DOCS_DIR)
    print(f"📄 加载到 {len(docs)} 个文档片段")

    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    print(f"✂️  切片后得到 {len(chunks)} 个 chunk")

    add_documents(chunks)
    after = vs._collection.count()
    print(f"✅ 入库完成，当前向量库共 {after} 条")


def test_rag_add_file():
    """测试增量添加单个文件"""
    file_path = input("请输入文件完整路径（如 ./uploads/考勤.txt）：")
    if not file_path.strip():
        print("⚠️ 路径不能为空")
        return
    try:
        count = rag_add_file(file_path)
        print(f"✅ 文件入库成功，新增 {count} 条向量")
    except Exception as e:
        print(f"❌ 入库失败：{str(e)}")


def test_rag_add_files():
    """测试批量添加文件"""
    paths_str = input("请输入多个文件路径，用逗号分隔：")
    if not paths_str.strip():
        print("⚠️ 路径不能为空")
        return
    file_paths = [p.strip() for p in paths_str.split(",")]
    print(f"📋 待处理 {len(file_paths)} 个文件...")
    result = rag_add_files(file_paths)
    print(f"✅ 成功 {len(result['success'])} 个，❌ 失败 {len(result['failed'])} 个")
    if result["failed"]:
        for f in result["failed"]:
            print(f"   失败：{f['path']} → {f['error']}")


def test_rag_delete_file():
    """测试删除文件"""
    file_path = input("请输入要删除的文件完整路径：")
    if not file_path.strip():
        print("⚠️ 路径不能为空")
        return
    rag_delete_file(file_path)
    print(f"✅ 已删除文件 {file_path} 的所有向量")


def test_rag_stats():
    """查看向量库统计"""
    vs = get_vector_store()
    total = vs._collection.count()
    print(f"📊 向量库统计：共 {total} 条向量")

    if total > 0:
        all_data = vs._collection.get(limit=10000)
        sources = set()
        for meta in all_data["metadatas"]:
            if meta and "source" in meta:
                sources.add(meta["source"])
        print(f"📁 涉及 {len(sources)} 个文件：")
        for s in sorted(sources):
            print(f"   - {s}")


def show_menu():
    print("\n========== RAG 功能测试菜单 ==========")
    print("1. RAG 问答测试")
    print("2. 全量入库测试")
    print("3. 单文件增量添加")
    print("4. 批量文件添加")
    print("5. 删除文件向量")
    print("6. 查看向量库统计")
    print("0. 退出测试程序")
    return input("请输入操作序号：")


def test_rag():
    print("🔌 RAG 测试环境已就绪")
    while True:
        opt = show_menu()
        try:
            if opt == "1":
                test_rag_search()
            elif opt == "2":
                test_rag_init()
            elif opt == "3":
                test_rag_add_file()
            elif opt == "4":
                test_rag_add_files()
            elif opt == "5":
                test_rag_delete_file()
            elif opt == "6":
                test_rag_stats()
            elif opt == "0":
                print("🛑 即将退出测试程序")
                break
            else:
                print("❌ 无效选项，请重新输入！")
        except Exception as e:
            print(f"❌ 【异常】{str(e)}")


if __name__ == "__main__":
    test_rag()