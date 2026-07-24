"""Extract Chinese characters and tech terms from blog articles for digital rain."""
import re
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Collect article body text from all blog posts
texts = []
for f in sorted(ROOT.glob("2021/*/*/*/index.html")):
    html = f.read_text(encoding="utf-8")
    # Strip HTML tags and scripts
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    texts.append(text)

# Extract unique Chinese characters
all_chars = set()
tech_terms = set()

for t in texts:
    for ch in t:
        if "一" <= ch <= "鿿" or "　" <= ch <= "〿":
            all_chars.add(ch)

# Extract 2-3 char meaningful tech terms
KEYWORDS = "启动线程内存组件源码流程生命周期数据存储观察性能优化回调消息队列调度任务初始注册拦截分发处理管理系统服务框架结构方法接口实现异步同步缓存回收引用堆栈上下文配置监听绑定解绑延迟执行广播接收继承构造参数返回调用销毁创建加载解析编码解码序列布局渲染测量绘制触摸事件通知校验版本代理工厂适配装饰责任链单例模式注解泛型反射代理静态动态内部匿名局部全局常量变量状态标记开关过滤排序查找遍历迭代聚合组合关联依赖映射转换拷贝克隆压缩展开嵌套递归循环跳转中断异常错误崩溃泄漏溢出越界安全权限认证授权加密解密签名验证令牌会话持久化序列化反序列化"
for t in texts:
    for i in range(len(t) - 1):
        seg = t[i : i + 2]
        if all("一" <= c <= "鿿" for c in seg):
            if any(kw in seg for kw in KEYWORDS.split("绑定解绑延迟执行广播接收继承构造参数返回调用销毁创建加载解析编码解码序列布局渲染测量绘制触摸事件通知校验版本代理工厂适配装饰")):
                tech_terms.add(seg)

# Pick representative chars
chars = random.sample(sorted(all_chars), min(100, len(all_chars)))
terms = random.sample(sorted(tech_terms), min(40, len(tech_terms)))

print("Unique Chinese chars found:", len(all_chars))
print("Tech terms found:", len(tech_terms))
print()
print("CHARS:")
print("".join(chars))
print()
print("TERMS:")
for t in terms:
    print(t)
