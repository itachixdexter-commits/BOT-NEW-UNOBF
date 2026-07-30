import subprocess
import os
import uuid
import re
import urllib.request

class LuaDeobfuscator:
    def __init__(self, work_dir="/tmp/lua_deobf"):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        
        # تحديد مجلد الأدوات وتحميلها إذا نقصت
        self.tools_dir = os.path.join(os.getcwd(), "tools")
        if not os.path.exists(self.tools_dir):
            os.makedirs(self.tools_dir)
        self.setup_tools()

    def setup_tools(self):
        """تحميل الأدوات الأساسية تلقائياً"""
        unluac_path = os.path.join(self.tools_dir, "unluac.jar")
        if not os.path.exists(unluac_path):
            print("Downloading unluac.jar...")
            url = "https://github.com/the-maldonado/unluac/raw/master/unluac.jar" # رابط مباشر ومستقر
            try:
                urllib.request.urlretrieve(url, unluac_path)
                print("unluac.jar downloaded successfully.")
            except:
                print("Failed to download unluac.jar automatically.")

    def save_temp_file(self, content, extension=".lua"):
        filename = f"{uuid.uuid4()}{extension}"
        path = os.path.join(self.work_dir, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def run_tool(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Error: {str(e)}"

    def deobfuscate_all(self, content):
        file_path = self.save_temp_file(content)
        results = {}
        
        # 1. محاولة فك البايت كود باستخدام Java
        unluac_path = os.path.join(self.tools_dir, "unluac.jar")
        if os.path.exists(unluac_path):
            results['Unluac (Decompiler)'] = self.run_tool(["java", "-jar", unluac_path, file_path])
        
        # 2. تحليل الـ VM والـ Constants (لـ MoonSec و WeAreDevs)
        results['Advanced VM Analysis'] = self.advanced_vm_analysis(content)
        
        # 3. محاولة التفكيك عبر نسخ Lua المختلفة
        for ver in ["5.1", "5.2", "5.3", "5.4"]:
            results[f'Lua {ver} Disassembly'] = self.run_tool([f"luac{ver}", "-l", "-l", file_path])

        if os.path.exists(file_path):
            os.remove(file_path)
        return results

    def advanced_vm_analysis(self, content):
        try:
            text = content.decode('utf-8', errors='ignore')
            report = "-- [Advanced VM Analysis Report]\n"
            
            # كشف الحمايات المعروفة
            if "MoonSec" in text: report += "-- Detected: MoonSec VM Protection\n"
            elif "Prometheus" in text: report += "-- Detected: Prometheus VM\n"
            elif "IronBrew" in text or "WeAreDevs" in text: report += "-- Detected: IronBrew / WeAreDevs VM\n"
            
            # استخراج النصوص المشفرة (Strings Extraction)
            strings = re.findall(r'\\(\d{1,3})', text)
            if strings:
                try:
                    extracted = "".join([chr(int(s)) for s in strings if int(s) < 256])
                    if len(extracted) > 10:
                        report += f"-- Extracted Strings: {extracted[:1000]}\n"
                except: pass
            
            return report + "\n-- Analysis Complete."
        except:
            return "-- Analysis Failed."
