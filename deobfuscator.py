import subprocess
import os
import uuid
import re

class LuaDeobfuscator:
    def __init__(self, work_dir="/tmp/lua_deobf"):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        self.tools_dir = os.path.join(os.getcwd(), "tools")

    def save_temp_file(self, content, extension=".lua"):
        filename = f"{uuid.uuid4()}{extension}"
        path = os.path.join(self.work_dir, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def run_tool(self, cmd):
        try:
            # محاولة تشغيل الأمر
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Tool Error: {str(e)}"

    def deobfuscate_all(self, content):
        file_path = self.save_temp_file(content)
        results = {}
        
        # 1. Unluac (أقوى أداة للبايت كود)
        unluac_path = os.path.join(self.tools_dir, "unluac.jar")
        if os.path.exists(unluac_path):
            results['Unluac (Decompiler)'] = self.run_tool(["java", "-jar", unluac_path, file_path])
        else:
            results['Unluac'] = "unluac.jar not found in tools folder."

        # 2. تحليل الـ VM (MoonSec, WeAreDevs, etc.)
        results['Advanced VM Analysis'] = self.advanced_vm_analysis(content)
        
        # 3. محاولة التفكيك عبر نسخ Lua (التأكد من الأسماء الصحيحة في Linux)
        for ver in ["5.1", "5.2", "5.3", "5.4"]:
            # في بعض الأنظمة يكون الاسم luac5.1 وفي بعضها luac51
            cmd = f"luac{ver}"
            res = self.run_tool([cmd, "-l", "-l", file_path])
            if "Tool Error" in res:
                cmd = f"luac{ver.replace('.', '')}"
                res = self.run_tool([cmd, "-l", "-l", file_path])
            results[f'Lua {ver} Analysis'] = res

        if os.path.exists(file_path):
            os.remove(file_path)
        return results

    def advanced_vm_analysis(self, content):
        try:
            text = content.decode('utf-8', errors='ignore')
            report = "-- [Mega VM Deobfuscator Engine]\n"
            
            # كشف الحمايات
            protections = {
                "MoonSec": ["MoonSec", "LUA_VM", "MoonV3"],
                "Prometheus": ["Prometheus", "LPH_"],
                "IronBrew/WeAreDevs": ["IronBrew", "IB_"],
                "MoonVeil": ["MoonVeil", "MV_"]
            }
            
            for name, keys in protections.items():
                if any(k in text for k in keys):
                    report += f"-- Detected Protection: {name}\n"

            # استخراج النصوص المشفرة (Strings) - منطق محسن
            # يبحث عن الأرقام المشفرة بـ XOR أو السلاسل النصية الطويلة
            found_strings = re.findall(r'\"[^\"]{10,}\"|\'[^\']{10,}\'', text)
            if found_strings:
                report += "-- Found Potential Constants:\n"
                for s in found_strings[:10]:
                    report += f"-- {s}\n"

            # استخراج قيم XOR
            xor_keys = re.findall(r'(\d{1,3})\s*\^\s*(\d{1,3})', text)
            if xor_keys:
                report += f"-- Found {len(xor_keys)} potential XOR operations.\n"

            return report + "\n-- Static Analysis Complete. If result is empty, script might be double-obfuscated."
        except:
            return "-- Analysis Failed."
