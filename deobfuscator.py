import subprocess
import os
import uuid
import re
import logging
from typing import Dict, List, Any, Optional
from luaparser import ast, astnodes

# إعداد التسجيل الاحترافي
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LuaProEngine")

class ConstantTransformer(ast.ASTTransformer):
    """محول AST لتبسيط العمليات الحسابية والمنطقية وتتبع القيم"""
    def __init__(self):
        super().__init__()
        self.symbols = {}

    def visit_LocalAssign(self, node):
        node.values = [self.visit(v) for v in node.values]
        # تتبع القيم الثابتة للمتغيرات المحلية (Constant Propagation)
        if len(node.targets) == len(node.values):
            for target, val in zip(node.targets, node.values):
                if isinstance(target, astnodes.Name):
                    if isinstance(val, (astnodes.Number, astnodes.String, astnodes.TrueExpr, astnodes.FalseExpr)):
                        self.symbols[target.id] = val
        return node

    def visit_Name(self, node):
        # استبدال المتغيرات بقيمها الثابتة
        if node.id in self.symbols:
            return self.symbols[node.id]
        return node

    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        if isinstance(node.left, astnodes.Number) and isinstance(node.right, astnodes.Number):
            l, r = node.left.n, node.right.n
            try:
                if isinstance(node.op, astnodes.AddOp): return astnodes.Number(l + r)
                if isinstance(node.op, astnodes.SubOp): return astnodes.Number(l - r)
                if isinstance(node.op, astnodes.MultOp): return astnodes.Number(l * r)
                if isinstance(node.op, astnodes.DivOp): return astnodes.Number(l / r)
            except: pass
        return node

class VariableRenamer(ast.ASTTransformer):
    """إعادة تسمية المتغيرات بناءً على النطاق بشكل بنيوي"""
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.mapping = {}
        self.reserved = {"string", "table", "math", "bit32", "pairs", "ipairs", "print", "load", "loadstring", "self"}

    def visit_Name(self, node):
        if node.id not in self.reserved and len(node.id) <= 2:
            if node.id not in self.mapping:
                self.counter += 1
                self.mapping[node.id] = f"var_{self.counter}"
            node.id = self.mapping[node.id]
        return node

class LuaDeobfuscator:
    def __init__(self, work_dir: str = "/tmp/lua_deobf"):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir): os.makedirs(self.work_dir)
        self.tools_dir = os.path.join(os.path.dirname(__file__), "tools")

    def structural_analysis(self, text: str) -> str:
        try:
            # تنظيف أولي للتعليقات
            text = re.sub(r'--.*', '', text)
            tree = ast.parse(text)
            
            # تطبيق المحولات البنيوية بشكل تكراري
            for _ in range(3):
                tree = ConstantTransformer().visit(tree)
                tree = VariableRenamer().visit(tree)
            
            return ast.to_lua_source(tree)
        except Exception as e:
            logger.error(f"AST Error: {e}")
            return text

    def deobfuscate_all(self, content: bytes) -> Dict[str, str]:
        text = content.decode('utf-8', errors='ignore')
        results = {}
        
        # 1. المحرك البنيوي (AST Analysis)
        results['Structural_Analysis'] = self.structural_analysis(text)
        
        # 2. فك طبقات loadstring (Peeling)
        peeled = text
        for _ in range(5):
            match = re.search(r'(?:loadstring|load)\s*\(\s*["\'](.*?)["\']\s*\)', peeled)
            if match:
                try:
                    inner = match.group(1).encode().decode('unicode_escape')
                    peeled = inner
                except: break
            else: break
        if peeled != text:
            results['Recursive_Peeling'] = peeled

        # 3. الأدوات الخارجية (Unluac)
        unluac_jar = os.path.join(self.tools_dir, "unluac.jar")
        if os.path.exists(unluac_jar):
            file_path = os.path.join(self.work_dir, f"{uuid.uuid4()}.lua")
            with open(file_path, "wb") as f: f.write(content)
            res = subprocess.run(["java", "-jar", unluac_jar, file_path], capture_output=True, text=True)
            if res.returncode == 0: results['Bytecode_Decompilation'] = res.stdout
            if os.path.exists(file_path): os.remove(file_path)

        return results
